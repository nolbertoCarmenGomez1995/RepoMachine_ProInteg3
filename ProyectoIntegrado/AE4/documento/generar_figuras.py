"""Genera las figuras y las cifras del documento final a partir de los mismos datos y funciones de la app.

Uso, desde la carpeta ProyectoIntegrado:
    python AE4/documento/generar_figuras.py

Lee AE3/resultados/ y escribe en AE4/documento/figuras/ las imágenes PNG y cifras_documento.json.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

DOC_DIR = Path(__file__).resolve().parent
APP_DIR = DOC_DIR.parent
PROJECT_DIR = APP_DIR.parent
RESULTS_DIR = PROJECT_DIR / "AE3" / "resultados"
FIGURAS_DIR = DOC_DIR / "figuras"

sys.path.insert(0, str(APP_DIR))
from dashboard import (  # noqa: E402
    AREA_AGIL,
    AREA_EXTENSA,
    ORDEN_AREAS,
    ORDEN_RANGOS,
    SIN_IDIOMA,
    cargar_libros,
    ranking_categoria,
    resumir_calificaciones,
    resumir_composicion_idioma,
    resumir_estadisticas_calificacion,
    resumir_formato,
    resumir_participacion,
    resumir_reparto_extension,
)

# Mismos colores por área que la app
COLORES_AREA = {AREA_AGIL: "#2a78d6", AREA_EXTENSA: "#eb6834"}
COLORES_RANGO = {"3,5 a 3,99": "#c6dbef", "4,0 a 4,49": "#6baed6", "4,5 a 5,0": "#08519c"}

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": 10,
    "axes.titlesize": 12,
    "axes.titleweight": "bold",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "figure.dpi": 150,
})


def miles(valor: float) -> str:
    return f"{valor:,.0f}".replace(",", ".")


def decimal(valor: float, decimales: int = 2) -> str:
    return f"{valor:,.{decimales}f}".replace(",", "§").replace(".", ",").replace("§", ".")


formato_miles = FuncFormatter(lambda valor, _: miles(valor))


def guardar(fig, nombre: str) -> None:
    fig.tight_layout()
    fig.savefig(FIGURAS_DIR / nombre, bbox_inches="tight")
    plt.close(fig)


def figura_poblacion(poblacion: pd.DataFrame) -> None:
    exclusiones = poblacion.iloc[1:7].copy()
    exclusiones = exclusiones.loc[~exclusiones["criterio"].str.startswith("Calificación >=")]
    exclusiones = exclusiones.iloc[::-1]
    etiquetas = {
        "Calificación faltante": "Calificación faltante",
        "Calificación < 3.5": "Calificación < 3,5",
        "Destacados con páginas faltantes": "Destacados sin páginas",
        "Destacados con páginas < 1": "Destacados con menos de 1 página",
        "Destacados con páginas > 5.000": "Destacados con más de 5.000 páginas",
    }
    fig, ax = plt.subplots(figsize=(8, 3.6))
    barras = ax.barh(exclusiones["criterio"].map(etiquetas), exclusiones["registros"], color="#7f8c8d")
    ax.bar_label(barras, labels=[miles(v) for v in exclusiones["registros"]], padding=3)
    ax.xaxis.set_major_formatter(formato_miles)
    ax.set_xlabel("Ediciones excluidas (registros)")
    ax.set_title("Ediciones excluidas por criterio (de 500.000 registros)")
    ax.set_xlim(0, exclusiones["registros"].max() * 1.18)
    guardar(fig, "f01_exclusiones_poblacion.png")


def figura_reparto(reparto: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    barras = ax.bar(reparto["categoria_extension"], reparto["obras_asignadas"],
                    color=[COLORES_AREA[a] for a in reparto["categoria_extension"]], width=0.55)
    ax.bar_label(barras, labels=[f"{miles(o)} obras\n({decimal(p)} %)" for o, p in
                                 zip(reparto["obras_asignadas"], reparto["porcentaje_obras"])], padding=3)
    ax.yaxis.set_major_formatter(formato_miles)
    ax.set_ylabel("Títulos únicos (obras)")
    ax.set_title("Títulos únicos por área de exhibición (umbral: 350 páginas)")
    ax.set_ylim(0, reparto["obras_asignadas"].max() * 1.25)
    guardar(fig, "f02_reparto_por_area.png")


def figura_sensibilidad(sensibilidad: pd.DataFrame) -> None:
    fig, ax = plt.subplots(figsize=(7, 3.8))
    for area in ORDEN_AREAS:
        datos = sensibilidad.loc[sensibilidad["categoria_extension"].eq(area)]
        ax.plot(datos["umbral_paginas"], datos["porcentaje_registros"], marker="o",
                color=COLORES_AREA[area], label=area)
        for x, y in zip(datos["umbral_paginas"], datos["porcentaje_registros"]):
            desplazamiento = 7 if area == AREA_AGIL else -14
            ax.annotate(f"{decimal(y, 1)} %", (x, y), textcoords="offset points", xytext=(0, desplazamiento),
                        ha="center", fontsize=8, color=COLORES_AREA[area])
    ax.axvline(350, color="#555555", linestyle="--", linewidth=1)
    ax.text(352, 50, "Umbral elegido\n(350 páginas)", fontsize=8, color="#555555", va="center")
    ax.set_xticks(sorted(sensibilidad["umbral_paginas"].unique()))
    ax.set_xlabel("Umbral de páginas")
    ax.set_ylabel("% de ediciones")
    ax.set_ylim(0, 100)
    ax.set_title("Sensibilidad del reparto al umbral de páginas")
    ax.legend(frameon=False, loc="upper left")
    guardar(fig, "f03_sensibilidad_umbral.png")


def figura_ranking(ranking: pd.DataFrame, columna: str, titulo: str, nombre: str, etiqueta: str) -> None:
    fig, ejes = plt.subplots(1, 2, figsize=(10, 4.6))
    for ax, area in zip(ejes, ORDEN_AREAS):
        datos = ranking.loc[ranking["categoria_extension"].eq(area)].iloc[::-1]
        barras = ax.barh(datos[columna], datos["obras_unicas"], color=COLORES_AREA[area])
        ax.bar_label(barras, labels=[f"{miles(o)} ({decimal(c)})" for o, c in
                                     zip(datos["obras_unicas"], datos["calificacion_promedio"])],
                     padding=3, fontsize=8)
        ax.xaxis.set_major_formatter(formato_miles)
        ax.set_xlim(0, datos["obras_unicas"].max() * 1.35)
        ax.set_title(area, color=COLORES_AREA[area])
        ax.set_xlabel("Títulos únicos (obras)")
        ax.tick_params(axis="y", labelsize=8)
    ejes[0].set_ylabel(etiqueta)
    fig.suptitle(titulo, fontweight="bold")
    fig.text(0.5, -0.02, "Etiqueta: títulos únicos (calificación promedio, escala de 1 a 5)",
             ha="center", fontsize=8, color="#555555")
    guardar(fig, nombre)


def figura_calificaciones(libros: pd.DataFrame, distribucion: pd.DataFrame) -> None:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))
    base = [0.0, 0.0]
    for rango in ORDEN_RANGOS:
        valores = [
            distribucion.loc[distribucion["categoria_extension"].eq(a) & distribucion["rango_calificacion"].eq(rango),
                             "porcentaje_registros"].sum()
            for a in ORDEN_AREAS
        ]
        barras = ax1.bar(ORDEN_AREAS, valores, bottom=base, color=COLORES_RANGO[rango], label=rango, width=0.55)
        ax1.bar_label(barras, labels=[f"{decimal(v, 1)} %" for v in valores], label_type="center",
                      fontsize=8, color="white" if rango != "3,5 a 3,99" else "#222222")
        base = [b + v for b, v in zip(base, valores)]
    ax1.set_ylabel("% de ediciones del área")
    ax1.set_ylim(0, 100)
    ax1.set_title("Ediciones por rango de calificación")
    ax1.legend(title="Rango", frameon=False, fontsize=8, title_fontsize=8, loc="upper center",
               bbox_to_anchor=(0.5, -0.1), ncol=3)
    cajas = ax2.boxplot([libros.loc[libros["categoria_extension"].eq(a), "average_rating"] for a in ORDEN_AREAS],
                        tick_labels=ORDEN_AREAS, showfliers=False, patch_artist=True, widths=0.5)
    for caja, area in zip(cajas["boxes"], ORDEN_AREAS):
        caja.set_facecolor(COLORES_AREA[area])
        caja.set_alpha(0.6)
    for mediana in cajas["medians"]:
        mediana.set_color("#222222")
    ax2.set_ylabel("Calificación promedio (escala 1 a 5)")
    ax2.set_ylim(3.45, 5.05)
    ax2.set_title("Mediana y cuartiles por área")
    guardar(fig, "f06_calificacion_por_area.png")


def figura_composicion(composicion: pd.DataFrame, principales: list[str]) -> pd.DataFrame:
    tabla = composicion.assign(
        grupo=composicion["idioma"].where(composicion["idioma"].isin([*principales, SIN_IDIOMA]), "Otros idiomas")
    ).groupby(["categoria_extension", "grupo"], as_index=False)["porcentaje_registros"].sum()
    orden = [*principales, "Otros idiomas", SIN_IDIOMA]
    colores = ["#1b4f72", "#2e86c1", "#5dade2", "#85c1e9", "#aed6f1", "#bfc9ca", "#e5e8e8"]
    fig, ax = plt.subplots(figsize=(10, 2.8))
    izquierda = [0.0, 0.0]
    for grupo, color in zip(orden, colores):
        valores = [tabla.loc[tabla["categoria_extension"].eq(a) & tabla["grupo"].eq(grupo),
                             "porcentaje_registros"].sum() for a in ORDEN_AREAS]
        barras = ax.barh(ORDEN_AREAS, valores, left=izquierda, color=color, label=grupo, height=0.55)
        ax.bar_label(barras, labels=[f"{decimal(v, 1)}" if v >= 2 else "" for v in valores],
                     label_type="center", fontsize=8, color="white" if grupo == principales[0] else "#222222")
        izquierda = [i + v for i, v in zip(izquierda, valores)]
    ax.invert_yaxis()
    ax.set_xlim(0, 100)
    ax.set_xlabel("% de ediciones del área (incluye ediciones sin idioma informado)")
    ax.set_title("Composición por idioma de cada área")
    ax.legend(ncol=7, frameon=False, fontsize=8, loc="upper center", bbox_to_anchor=(0.5, -0.35))
    guardar(fig, "f07_composicion_idioma.png")
    return tabla


def figura_participacion(participacion: pd.DataFrame, reparto: pd.DataFrame) -> None:
    medidas = {
        "% de obras": reparto.set_index("categoria_extension")["porcentaje_obras"],
        "% de calificaciones": participacion.set_index("categoria_extension")["porcentaje_calificaciones"],
        "% de reseñas": participacion.set_index("categoria_extension")["porcentaje_resenas"],
    }
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ancho = 0.36
    posiciones = range(len(medidas))
    for desplazamiento, area in zip((-ancho / 2, ancho / 2), ORDEN_AREAS):
        valores = [serie[area] for serie in medidas.values()]
        barras = ax.bar([p + desplazamiento for p in posiciones], valores, width=ancho,
                        color=COLORES_AREA[area], label=area)
        ax.bar_label(barras, labels=[f"{decimal(v, 1)} %" for v in valores], padding=2, fontsize=8)
    ax.set_xticks(list(posiciones), list(medidas))
    ax.set_ylim(0, 100)
    ax.set_ylabel("Participación del total (%)")
    ax.set_title("Obras frente a calificaciones y reseñas por área (una edición por obra)")
    ax.legend(frameon=False)
    guardar(fig, "f08_participacion_lectores.png")


def figura_formato(formato: pd.DataFrame) -> None:
    orden = (formato.groupby("formato_grupo")["registros_edicion"].sum().sort_values(ascending=False).index.tolist())
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ancho = 0.38
    for desplazamiento, area in zip((-ancho / 2, ancho / 2), ORDEN_AREAS):
        datos = formato.loc[formato["categoria_extension"].eq(area)].set_index("formato_grupo").reindex(orden)
        barras = ax.bar([i + desplazamiento for i in range(len(orden))], datos["porcentaje_registros"],
                        width=ancho, color=COLORES_AREA[area], label=area)
        ax.bar_label(barras, labels=[f"{decimal(v, 1)}" for v in datos["porcentaje_registros"]], padding=2, fontsize=7)
    ax.set_xticks(range(len(orden)), orden)
    ax.set_ylabel("% de ediciones del área")
    ax.set_title("Composición por formato de cada área")
    ax.legend(frameon=False)
    guardar(fig, "f09_formato_por_area.png")


def main() -> None:
    FIGURAS_DIR.mkdir(parents=True, exist_ok=True)
    libros = cargar_libros(RESULTS_DIR / "libros_preparados_enriquecidos.csv")
    poblacion = pd.read_csv(RESULTS_DIR / "t1_control_poblacion.csv", encoding="utf-8")
    sensibilidad = pd.read_csv(RESULTS_DIR / "t2b_sensibilidad_umbral.csv", encoding="utf-8")

    # Mismas funciones y población sin filtros que la app
    reparto = resumir_reparto_extension(libros)
    editoriales = ranking_categoria(libros, "publisher")
    idiomas = ranking_categoria(libros, "idioma_normalizado")
    distribucion = resumir_calificaciones(libros)
    estadisticas = resumir_estadisticas_calificacion(libros).set_index("categoria_extension").reindex(ORDEN_AREAS)
    composicion = resumir_composicion_idioma(libros)
    participacion = resumir_participacion(libros)
    formato = resumir_formato(libros)
    principales = libros["idioma_normalizado"].value_counts().head(5).index.tolist()

    figura_poblacion(poblacion)
    figura_reparto(reparto)
    figura_sensibilidad(sensibilidad)
    figura_ranking(editoriales, "publisher", "Diez editoriales con más títulos únicos por área",
                   "f04_top_editoriales.png", "Editorial")
    figura_ranking(idiomas, "idioma_normalizado", "Diez idiomas con más títulos únicos por área",
                   "f05_top_idiomas.png", "Idioma")
    figura_calificaciones(libros, distribucion)
    composicion_agrupada = figura_composicion(composicion, principales)
    figura_participacion(participacion, reparto)
    figura_formato(formato)

    cifras = {
        "poblacion": poblacion.to_dict(orient="records"),
        "total_registros": len(libros),
        "total_obras": int(libros["work_id"].nunique()),
        "calificacion_media_global": round(float(libros["average_rating"].mean()), 4),
        "mediana_paginas_global": float(libros["pages"].median()),
        "reparto": reparto.round(4).to_dict(orient="records"),
        "sensibilidad": sensibilidad.to_dict(orient="records"),
        "editoriales": editoriales.round(4).to_dict(orient="records"),
        "idiomas": idiomas.round(4).to_dict(orient="records"),
        "calificacion_rangos": distribucion.round(4).to_dict(orient="records"),
        "calificacion_estadisticas": estadisticas.round(4).reset_index().to_dict(orient="records"),
        "composicion_idioma": composicion_agrupada.round(4).to_dict(orient="records"),
        "idiomas_principales": principales,
        "participacion": participacion.round(4).to_dict(orient="records"),
        "formato": formato.round(4).to_dict(orient="records"),
    }
    (FIGURAS_DIR / "cifras_documento.json").write_text(
        json.dumps(cifras, ensure_ascii=False, indent=1, default=float), encoding="utf-8"
    )
    print(f"Figuras y cifras generadas en {FIGURAS_DIR.relative_to(PROJECT_DIR).as_posix()}")


if __name__ == "__main__":
    main()
