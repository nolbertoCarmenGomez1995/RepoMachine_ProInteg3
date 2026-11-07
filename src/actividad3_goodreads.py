"""Flujo reproducible de la Actividad 3: segmentación de libros Goodreads."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from joblib import dump
from sklearn.cluster import KMeans
from sklearn.impute import SimpleImputer
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .goodreads import goodreads_quality_audit, prepare_goodreads_frame
from .hf_loader import HFDatasetLoader


BUSINESS_QUESTION = (
    "Entre los libros de Goodreads con calificacion promedio igual o superior "
    "a 3.5, que perfiles de extension fisica y participacion de lectores se "
    "pueden identificar para orientar como una libreria distribuye su espacio "
    "de exhibicion y prioriza su curaduria?"
)
DATASET_ID = "pfaha/goodreads-books"
DATASET_URL = "https://huggingface.co/datasets/pfaha/goodreads-books"
FEATURE_COLUMNS = [
    "paginas",
    "calificacion",
    "log1p_cantidad_calificaciones",
    "log1p_cantidad_resenas",
]
K_VALUES = range(2, 7)
SEED = 42
SAMPLE_SIZE = 20_000
VALIDATION_SIZE = 4_000
MIN_PAGES = 20


def _require_columns(frame: pd.DataFrame, columns: set[str]) -> None:
    missing = columns.difference(frame.columns)
    if missing:
        raise KeyError(f"Faltan columnas necesarias: {sorted(missing)}.")


def prepare_clustering_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Prepara registros válidos para segmentación y devuelve cifras de auditoría."""
    audit = goodreads_quality_audit(raw)
    books = prepare_goodreads_frame(
        raw,
        minimum_rating=3.5,
        maximum_rating=5.0,
        deduplicate_text=False,
    )
    _require_columns(
        books,
        {
            "titulo",
            "autor",
            "paginas",
            "calificacion",
            "cantidad_calificaciones",
            "cantidad_resenas",
        },
    )

    identity_columns = [
        "titulo",
        "autor",
        "paginas",
        "calificacion",
        "cantidad_calificaciones",
        "cantidad_resenas",
    ]
    duplicate_count = int(books.duplicated(subset=identity_columns).sum())
    books = books.drop_duplicates(subset=identity_columns).reset_index(drop=True)

    positive_pages = books.loc[books["paginas"].ge(MIN_PAGES), "paginas"]
    if positive_pages.empty:
        raise ValueError("No hay libros con un número de páginas válido.")
    q1 = float(positive_pages.quantile(0.25))
    q3 = float(positive_pages.quantile(0.75))
    upper_fence = q3 + 1.5 * (q3 - q1)

    page_valid = books["paginas"].between(MIN_PAGES, upper_fence)
    eligible = books.loc[page_valid].copy()
    if eligible.empty:
        raise ValueError("La limpieza de páginas no dejó libros para segmentar.")

    for column in ("cantidad_calificaciones", "cantidad_resenas"):
        values = pd.to_numeric(eligible[column], errors="coerce")
        values = values.where(np.isfinite(values) & values.ge(0))
        eligible[column] = values

    eligible["log1p_cantidad_calificaciones"] = np.log1p(
        eligible["cantidad_calificaciones"]
    )
    eligible["log1p_cantidad_resenas"] = np.log1p(eligible["cantidad_resenas"])

    counts = {
        "raw_rows": len(raw),
        "after_essential_cleaning": len(books) + duplicate_count,
        "exact_duplicates_removed": duplicate_count,
        "after_deduplication": len(books),
        "invalid_pages_removed": int((~page_valid).sum()),
        "eligible_rows": len(eligible),
        "pages_q1": q1,
        "pages_q3": q3,
        "pages_upper_fence": upper_fence,
        "audit": audit,
    }
    return eligible.reset_index(drop=True), counts


def _make_pipeline(k: int) -> Pipeline:
    return Pipeline(
        [
            ("imputacion", SimpleImputer(strategy="median", add_indicator=True)),
            ("escalado", StandardScaler()),
            (
                "kmeans",
                KMeans(n_clusters=k, n_init=10, random_state=SEED),
            ),
        ]
    )


def fit_and_evaluate(
    books: pd.DataFrame,
    *,
    sample_size: int = SAMPLE_SIZE,
    validation_size: int = VALIDATION_SIZE,
) -> dict[str, Any]:
    """Selecciona k por silhouette y asigna todos los libros a un segmento."""
    _require_columns(books, set(FEATURE_COLUMNS))
    if len(books) < 10:
        raise ValueError("Se necesitan al menos 10 libros para evaluar K-Means.")
    if sample_size < 10 or validation_size < 2:
        raise ValueError("Las muestras de entrenamiento y validación son demasiado pequeñas.")

    sample = books.sample(n=min(sample_size, len(books)), random_state=SEED)
    train_size = len(sample) - min(validation_size, max(2, len(sample) // 4))
    if train_size < 8:
        raise ValueError("No hay suficientes libros para entrenar y validar K-Means.")
    training, validation = train_test_split(
        sample,
        train_size=train_size,
        random_state=SEED,
    )
    x_train = training[FEATURE_COLUMNS]
    x_validation = validation[FEATURE_COLUMNS]

    candidates: list[dict[str, float | int]] = []
    for k in K_VALUES:
        if k >= len(training):
            continue
        pipeline = _make_pipeline(k)
        pipeline.fit(x_train)
        validation_labels = pipeline.predict(x_validation)
        if np.unique(validation_labels).size < 2:
            score = float("nan")
            db_score = float("nan")
        else:
            validation_scaled = pipeline[:-1].transform(x_validation)
            score = float(silhouette_score(validation_scaled, validation_labels))
            db_score = float(davies_bouldin_score(validation_scaled, validation_labels))
        candidates.append(
            {
                "k": k,
                "silhouette": score,
                "davies_bouldin": db_score,
                "inercia_entrenamiento": float(pipeline.named_steps["kmeans"].inertia_),
            }
        )

    scores = pd.DataFrame(candidates).dropna(subset=["silhouette"])
    if scores.empty:
        raise ValueError("No se pudo evaluar ningún valor de k con silhouette.")
    best_k = int(scores.loc[scores["silhouette"].idxmax(), "k"])
    best_pipeline = _make_pipeline(best_k)
    best_pipeline.fit(x_train)

    all_labels = best_pipeline.predict(books[FEATURE_COLUMNS])
    labeled_books = books.copy()
    labeled_books["segmento"] = all_labels
    validation_labels = best_pipeline.predict(x_validation)
    validation_scaled = best_pipeline[:-1].transform(x_validation)
    metrics = {
        "best_k": best_k,
        "silhouette": float(silhouette_score(validation_scaled, validation_labels)),
        "davies_bouldin": float(
            davies_bouldin_score(validation_scaled, validation_labels)
        ),
        "inertia": float(best_pipeline.named_steps["kmeans"].inertia_),
        "training_rows": len(training),
        "validation_rows": len(validation),
    }
    return {
        "model": best_pipeline,
        "books": labeled_books,
        "scores": scores.sort_values("k").reset_index(drop=True),
        "metrics": metrics,
    }


def _top_values(series: pd.Series, count: int = 3) -> str:
    values = series.dropna().astype(str).str.strip()
    values = values[values.ne("")]
    top = values.value_counts().head(count)
    if top.empty:
        return "Sin datos disponibles"
    return "; ".join(f"{name} ({quantity:,})" for name, quantity in top.items())


def build_cluster_profile(books: pd.DataFrame) -> pd.DataFrame:
    """Describe el tamaño y las variables de negocio de cada segmento."""
    records: list[dict[str, Any]] = []
    median_pages = float(books["paginas"].median())
    median_ratings = float(books["cantidad_calificaciones"].median())
    for segment, group in books.groupby("segmento", sort=True):
        pages_median = float(group["paginas"].median())
        ratings_median = float(group["cantidad_calificaciones"].median())
        length_profile = "mayor extensión" if pages_median > median_pages else "menor extensión"
        engagement_profile = (
            "mayor participación"
            if ratings_median > median_ratings
            else "menor participación"
        )
        record: dict[str, Any] = {
            "segmento": int(segment),
            "perfil": f"{length_profile}, {engagement_profile}",
            "libros": len(group),
            "participacion_pct": 100 * len(group) / len(books),
            "paginas_mediana": pages_median,
            "calificacion_media": float(group["calificacion"].mean()),
            "calificaciones_mediana": ratings_median,
            "resenas_mediana": float(group["cantidad_resenas"].median()),
        }
        if "es_serie" in group:
            series = group["es_serie"].astype("string").str.lower()
            series_share = series.isin({"true", "1", "yes"}).mean()
            record["series_pct"] = 100 * float(series_share)
        if "editorial" in group:
            record["editoriales_top"] = _top_values(group["editorial"])
        if "idioma" in group:
            record["idiomas_top"] = _top_values(group["idioma"])
        records.append(record)
    return pd.DataFrame(records)


def _write_outputs(
    books: pd.DataFrame,
    counts: dict[str, Any],
    result: dict[str, Any],
    output_dir: Path,
    model_dir: Path,
) -> tuple[Path, Path, list[Path], Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    figure_dir = output_dir / "figuras"
    figure_dir.mkdir(parents=True, exist_ok=True)
    profile = build_cluster_profile(result["books"])
    metrics = result["metrics"]
    run_date = datetime.now().astimezone().isoformat(timespec="seconds")
    largest_segment = profile.loc[profile["participacion_pct"].idxmax()]
    highest_engagement_segment = profile.loc[
        profile["calificaciones_mediana"].idxmax()
    ]

    silhouette_path = figure_dir / "seleccion_k_silhouette.png"
    fig, ax = plt.subplots(figsize=(7, 4))
    ax.plot(result["scores"]["k"], result["scores"]["silhouette"], marker="o")
    ax.set(
        xlabel="Número de segmentos (k)",
        ylabel="Silhouette en validación",
        title="Selección de k para K-Means",
    )
    ax.set_xticks(result["scores"]["k"])
    ax.grid(alpha=0.25)
    fig.tight_layout()
    fig.savefig(silhouette_path, dpi=150)
    plt.close(fig)

    scatter_path = figure_dir / "segmentos_goodreads.png"
    plot_data = result["books"].sample(
        n=min(8_000, len(result["books"])), random_state=SEED
    )
    fig, ax = plt.subplots(figsize=(8, 5))
    scatter = ax.scatter(
        plot_data["paginas"],
        plot_data["calificacion"],
        c=plot_data["segmento"],
        cmap="viridis",
        s=10,
        alpha=0.55,
    )
    ax.set(
        xlabel="Páginas (libros válidos)",
        ylabel="Calificación promedio",
        title="Segmentos de libros Goodreads (muestra visual)",
    )
    fig.colorbar(scatter, ax=ax, label="Segmento")
    fig.tight_layout()
    fig.savefig(scatter_path, dpi=150)
    plt.close(fig)

    summary_path = output_dir / "actividad3_goodreads.txt"
    summary_lines = [
        "RESUMEN AUTOMÁTICO — ACTIVIDAD 3 GOODREADS",
        "=" * 58,
        f"Fecha de ejecución: {run_date}",
        f"Pregunta de negocio: {BUSINESS_QUESTION}",
        "Beneficiario: equipo hipotético de compras y exhibición de Librerías Plaza Lectura.",
        "Decisión apoyada: usar perfiles de libros como referencia inicial para curar el catálogo y planear exhibición.",
        f"Dataset: {DATASET_ID} ({DATASET_URL}), split train de Hugging Face.",
        "Tipo de aprendizaje: no supervisado.",
        "Algoritmo: K-Means.",
        f"Variables: {', '.join(FEATURE_COLUMNS)}.",
        "Preprocesamiento: rating entre 3.5 y 5; páginas >= 20 y <= valla superior IQR; "
        "eliminación de filas duplicadas en título, autor y variables del análisis; "
        "log1p en conteos de calificaciones/reseñas; imputación mediana y escalado "
        "ajustados solo en la muestra de entrenamiento.",
        f"Filas originales: {counts['raw_rows']:,}.",
        f"Filas elegibles tras limpieza: {counts['eligible_rows']:,}.",
        f"Duplicados exactos eliminados: {counts['exact_duplicates_removed']:,}.",
        f"Filas excluidas por páginas inválidas/fuera de IQR: {counts['invalid_pages_removed']:,}.",
        f"Valla superior IQR de páginas: {counts['pages_upper_fence']:.2f}.",
        "",
        "AUDITORÍA DEL DATASET ORIGINAL",
        counts["audit"].to_string(index=False),
        f"Configuración: semilla={SEED}; muestra máxima={SAMPLE_SIZE:,}; "
        f"entrenamiento={metrics['training_rows']:,}; validación={metrics['validation_rows']:,}; "
        f"k probado={list(map(int, result['scores']['k']))}.",
        f"Parámetros K-Means: k={metrics['best_k']}; n_init=10; random_state={SEED}.",
        f"Silhouette (validación): {metrics['silhouette']:.4f}.",
        f"Davies-Bouldin (validación): {metrics['davies_bouldin']:.4f}.",
        f"Inercia (entrenamiento): {metrics['inertia']:.4f}.",
        "",
        "PERFILES DE SEGMENTOS",
        profile.to_string(index=False),
        "",
        "Interpretación: los perfiles describen libros bien valorados en Goodreads, "
        "no ventas ni demanda observada de una librería.",
    ]
    summary_path.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")

    if metrics["silhouette"] < 0.25:
        reliability = (
            "La separación por silhouette es débil; los segmentos deben tratarse "
            "como una exploración, no como categorías comerciales consolidadas."
        )
    elif metrics["silhouette"] < 0.5:
        reliability = (
            "La separación es moderada; los perfiles sirven como hipótesis de "
            "curaduría que conviene validar con datos reales de ventas e inventario."
        )
    else:
        reliability = (
            "La separación observada es relativamente clara para las variables "
            "elegidas, pero aún debe validarse con ventas e inventario locales."
        )

    findings_path = output_dir / "hallazgos_actividad3.md"
    findings = [
        "# Hallazgos — Actividad 3: segmentos de libros Goodreads",
        "",
        f"**Pregunta:** {BUSINESS_QUESTION}",
        "",
        "El análisis se plantea para el equipo de compras y exhibición de "
        "Librerías Plaza Lectura, en un escenario académico hipotético.",
        "",
        "## Resultado del modelo",
        "",
        f"K-Means seleccionó **k = {metrics['best_k']}** entre los valores probados "
        f"({', '.join(map(str, result['scores']['k']))}), usando silhouette en una "
        "muestra de validación que no participó en el ajuste.",
        f"- Silhouette de validación: **{metrics['silhouette']:.3f}**.",
        f"- Davies–Bouldin de validación: **{metrics['davies_bouldin']:.3f}** "
        "(menor suele indicar segmentos más compactos y separados).",
        f"- Silhouette cerca de 1 indica segmentos compactos y separados; cerca de "
        f"0 indica solapamiento. {reliability}",
        "",
        "## Perfiles identificados",
        "",
        profile.to_markdown(index=False, floatfmt=".2f"),
        "",
        f"El segmento **{int(largest_segment['segmento'])}** es el más numeroso "
        f"({largest_segment['participacion_pct']:.1f}% de los registros) y su perfil "
        f"es *{largest_segment['perfil']}*, con una mediana de "
        f"{largest_segment['paginas_mediana']:.0f} páginas y "
        f"{largest_segment['calificaciones_mediana']:.0f} calificaciones por libro.",
        f"El segmento **{int(highest_engagement_segment['segmento'])}** registra la "
        f"mayor mediana de participación ({highest_engagement_segment['calificaciones_mediana']:.0f} "
        f"calificaciones y {highest_engagement_segment['resenas_mediana']:.0f} reseñas por libro); "
        f"su perfil es *{highest_engagement_segment['perfil']}*.",
        "",
        "La proporción de libros de cada segmento puede servir como punto de partida "
        "para conversar sobre curaduría y exhibición. No equivale directamente a "
        "metros lineales de estante: el dataset no contiene dimensiones físicas "
        "del mobiliario, ventas ni disponibilidad local.",
        "",
        "![Comparación de silhouette por k](figuras/seleccion_k_silhouette.png)",
        "",
        "![Libros por páginas, calificación y segmento](figuras/segmentos_goodreads.png)",
        "",
        "## Recomendación y límites",
        "",
        f"Empezar la conversación de exhibición con el segmento más numeroso "
        f"({int(largest_segment['segmento'])}, {largest_segment['participacion_pct']:.1f}%) "
        f"y revisar por separado el segmento con mayor participación de lectores "
        f"({int(highest_engagement_segment['segmento'])}). Contrastar ambos perfiles "
        "con ventas, rotación, costos, idioma y espacio real antes de cambiar compras "
        "o estantes. Las editoriales e idiomas de la tabla son descripciones posteriores "
        "de cada segmento, no variables que determinaron los grupos.",
        "",
        "El análisis se limita al split `train` de `pfaha/goodreads-books` y a "
        "calificaciones >= 3.5; por tanto, no describe todos los libros ni la demanda "
        "de una librería. K-Means depende de las variables, los filtros, el escalado "
        "y la semilla. Los perfiles son asociaciones descriptivas, no causas.",
        "",
        "Los valores de este documento se generan desde la misma ejecución que "
        "`actividad3_goodreads.txt`; no deben reemplazarse por cifras copiadas "
        "de ejecuciones anteriores.",
    ]
    findings_path.write_text("\n".join(findings) + "\n", encoding="utf-8")

    model_dir.mkdir(parents=True, exist_ok=True)
    model_path = model_dir / "kmeans_actividad3_goodreads.joblib"
    dump(result["model"], model_path)
    return summary_path, findings_path, [silhouette_path, scatter_path], model_path


def run_analysis(
    raw: pd.DataFrame,
    *,
    output_dir: str | Path,
    model_dir: str | Path,
    sample_size: int = SAMPLE_SIZE,
    validation_size: int = VALIDATION_SIZE,
) -> dict[str, Any]:
    """Ejecuta limpieza, selección/evaluación de K-Means y genera evidencias."""
    books, counts = prepare_clustering_data(raw)
    result = fit_and_evaluate(
        books,
        sample_size=sample_size,
        validation_size=validation_size,
    )
    summary, findings, figures, model_path = _write_outputs(
        books,
        counts,
        result,
        Path(output_dir),
        Path(model_dir),
    )
    return {
        **result,
        "counts": counts,
        "profile": build_cluster_profile(result["books"]),
        "summary_path": summary,
        "findings_path": findings,
        "figures": figures,
        "model_path": model_path,
    }


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    loader = HFDatasetLoader(dataset_name=DATASET_ID, split="train")
    raw = loader.load()
    print(f"Dataset: {raw.shape[0]:,} filas × {raw.shape[1]} columnas")
    print("Tipos de datos:\n", raw.dtypes.to_string())
    print("Muestra del dataset:\n", raw.head(3).to_string(index=False))
    print("Auditoría de calidad:\n", goodreads_quality_audit(raw).to_string(index=False))

    result = run_analysis(
        raw,
        output_dir=project_root / "reportes",
        model_dir=project_root / "modelos" / "libros",
    )
    print("Evaluación de k:\n", result["scores"].to_string(index=False))
    print("Perfil de segmentos:\n", result["profile"].to_string(index=False))
    print(f"Resumen: {result['summary_path']}")
    print(f"Hallazgos: {result['findings_path']}")
    print(f"Modelo: {result['model_path']}")


if __name__ == "__main__":
    main()
