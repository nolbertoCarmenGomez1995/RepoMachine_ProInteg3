"""Preparación y auditoría del conjunto Goodreads Books."""
from __future__ import annotations

import numpy as np
import pandas as pd


_COLUMN_NAMES = {
    "title": "titulo",
    "first_author": "autor",
    "pages": "paginas",
    "average_rating": "calificacion",
    "publisher": "editorial",
    "language": "idioma",
    "ratings_count": "cantidad_calificaciones",
    "reviews_count": "cantidad_resenas",
    "num_editions": "cantidad_ediciones",
    "is_part_of_series": "es_serie",
    "publication_date": "fecha_publicacion",
}
_REQUIRED_COLUMNS = {"title", "first_author", "pages", "average_rating"}
_NUMERIC_COLUMNS = {
    "paginas",
    "calificacion",
    "cantidad_calificaciones",
    "cantidad_resenas",
    "cantidad_ediciones",
}


def _as_text(value: object) -> str:
    if isinstance(value, (list, tuple, np.ndarray)):
        return ", ".join(str(part) for part in value)
    if pd.isna(value):
        return ""
    return str(value)


def _as_optional_text(value: object) -> object:
    if isinstance(value, (list, tuple, np.ndarray)):
        return ", ".join(str(part) for part in value)
    if pd.isna(value):
        return np.nan
    return str(value).strip()


def prepare_goodreads_frame(
    raw: pd.DataFrame,
    *,
    minimum_rating: float = 3.5,
    maximum_rating: float = 5.0,
    deduplicate_text: bool = False,
) -> pd.DataFrame:
    """Normaliza las columnas principales y conserva faltantes no esenciales."""
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("raw debe ser un pandas.DataFrame.")
    if not 0 <= minimum_rating <= maximum_rating <= 5:
        raise ValueError("El rango de calificación debe estar entre 0 y 5.")

    missing = _REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise KeyError(f"Faltan columnas requeridas de Goodreads: {sorted(missing)}.")

    selected = [column for column in _COLUMN_NAMES if column in raw.columns]
    frame = raw[selected].rename(columns=_COLUMN_NAMES).copy()
    for column in ("titulo", "autor"):
        frame[column] = frame[column].map(_as_text).str.strip()
    for column in ("editorial", "idioma", "fecha_publicacion"):
        if column in frame.columns:
            frame[column] = frame[column].map(_as_optional_text)
    for column in _NUMERIC_COLUMNS.intersection(frame.columns):
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame = frame.dropna(subset=["titulo", "autor", "calificacion"])
    frame = frame[
        frame["titulo"].ne("")
        & frame["autor"].ne("")
        & frame["calificacion"].between(minimum_rating, maximum_rating)
    ].copy()
    frame["texto"] = (
        frame["titulo"] + " " + frame["autor"]
    ).str.replace(r"\s+", " ", regex=True).str.strip()
    frame = frame[frame["texto"].ne("")]
    if deduplicate_text:
        frame = frame.drop_duplicates(subset="texto")
    return frame.reset_index(drop=True)


def goodreads_quality_audit(raw: pd.DataFrame) -> pd.DataFrame:
    """Resume faltantes, duplicados y anomalías numéricas sin alterar los datos."""
    if not isinstance(raw, pd.DataFrame):
        raise TypeError("raw debe ser un pandas.DataFrame.")
    missing = _REQUIRED_COLUMNS.difference(raw.columns)
    if missing:
        raise KeyError(f"Faltan columnas requeridas de Goodreads: {sorted(missing)}.")

    pages = pd.to_numeric(raw["pages"], errors="coerce")
    positive_pages = pages[np.isfinite(pages) & pages.gt(0)]
    page_limit = float(positive_pages.quantile(0.99)) if not positive_pages.empty else np.nan
    title = raw["title"].map(_as_text).str.strip()
    author = raw["first_author"].map(_as_text).str.strip()
    text = (title + " " + author).str.replace(r"\s+", " ", regex=True).str.strip()
    ratings = pd.to_numeric(raw["average_rating"], errors="coerce")

    rows: list[tuple[str, object]] = [
        ("Filas originales", len(raw)),
        ("Títulos vacíos o nulos", int(title.eq("").sum())),
        ("Autores vacíos o nulos", int(author.eq("").sum())),
        ("Calificaciones nulas o no numéricas", int(ratings.isna().sum())),
        (
            "Calificaciones fuera de [0, 5]",
            int((ratings.notna() & ~ratings.between(0, 5)).sum()),
        ),
        ("Páginas nulas o no numéricas", int(pages.isna().sum())),
        ("Libros con páginas <= 0", int((pages.notna() & pages.le(0)).sum())),
        ("Páginas positivas sobre el percentil 99", 0),
        ("Textos título+autor repetidos", int(text[text.ne("")].duplicated().sum())),
        ("Percentil 99 de páginas positivas", page_limit),
    ]
    if np.isfinite(page_limit):
        rows[7] = (
            "Páginas positivas sobre el percentil 99",
            int((pages.gt(page_limit) & np.isfinite(pages)).sum()),
        )
    return pd.DataFrame(rows, columns=["indicador", "valor"])
