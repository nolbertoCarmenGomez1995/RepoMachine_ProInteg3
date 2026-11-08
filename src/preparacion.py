from __future__ import annotations

from collections.abc import Iterable

import numpy as np
import pandas as pd

AREA_AGIL = "Lecturas Ágiles"
AREA_EXTENSA = "Obras extensas"
ORDEN_AREAS = [AREA_AGIL, AREA_EXTENSA]

ORDEN_RANGOS_CALIFICACION = ["3,5 a 3,99", "4,0 a 4,49", "4,5 a 5,0"]

# Palabras clave para agrupar los formatos escritos libremente en la fuente.
# El orden importa: se asigna el primer grupo cuyo patrón coincide.
_PATRONES_FORMATO = [
    ("Audio", ("audio", "mp3", "audible")),
    ("Digital", ("kindle", "ebook", "e-book", "nook", "digital", "download", "cd-rom", "dvd-rom")),
    ("Tapa dura", (
        "hardcover", "hard cover", "hardback", "library binding", "leather", "cloth", "board book",
        "turtleback", "textbook binding", "gebunden", "relié", "capa dura", "tapa dura",
    )),
    ("Tapa blanda", (
        "paperback", "softcover", "soft cover", "softback", "paper", "pocket", "bunko", "文庫",
        "shinsho", "broché", "brochura", "broschiert", "poche", "taschenbuch", "capa mole",
        "tapa blanda", "rústica",
        "chapbook", "pamphlet", "mass market",
    )),
]
_FORMATOS_SIN_INFORMAR = {"", "unknown", "unknown binding"}


def filtrar_poblacion(
    df: pd.DataFrame,
    calificacion_minima: float = 3.5,
    paginas_min: int = 1,
    paginas_max: int = 5000,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Devuelve los libros destacados con páginas válidas y la tabla de control de exclusiones."""
    destacados = df.loc[df["average_rating"].ge(calificacion_minima)]
    paginas_validas = destacados["pages"].between(paginas_min, paginas_max, inclusive="both")
    poblacion = destacados.loc[paginas_validas].copy()

    control = pd.DataFrame({
        "criterio": [
            "Dataset original",
            "Calificación faltante",
            f"Calificación < {calificacion_minima}",
            f"Calificación >= {calificacion_minima} (destacados)",
            "Destacados con páginas faltantes",
            f"Destacados con páginas < {paginas_min}",
            f"Destacados con páginas > {paginas_max:,}".replace(",", "."),
            f"Población final: destacados con páginas entre {paginas_min} y {paginas_max:,}".replace(",", "."),
        ],
        "registros": [
            len(df),
            int(df["average_rating"].isna().sum()),
            int(df["average_rating"].lt(calificacion_minima).sum()),
            len(destacados),
            int(destacados["pages"].isna().sum()),
            int(destacados["pages"].lt(paginas_min).sum()),
            int(destacados["pages"].gt(paginas_max).sum()),
            len(poblacion),
        ],
    })
    control["porcentaje_del_dataset"] = (control["registros"] / len(df) * 100).round(2)
    return poblacion, control


def clasificar_extension(paginas: pd.Series, umbral: int = 350) -> pd.Series:
    """Asigna el área de exhibición: hasta `umbral` páginas es lectura ágil, por encima es obra extensa."""
    return pd.Series(
        np.where(paginas.le(umbral), AREA_AGIL, AREA_EXTENSA), index=paginas.index
    )


def limpiar_categoria(serie: pd.Series) -> pd.Series:
    """Quita espacios externos y convierte los textos vacíos en nulos, sin cambiar el contenido."""
    limpia = serie.astype("string").str.strip()
    return limpia.mask(limpia.eq(""))


def normalizar_idioma(serie: pd.Series) -> pd.Series:
    """Unifica etiquetas equivalentes conservando el primer nombre: 'Spanish; Castilian' -> 'Spanish'."""
    return limpiar_categoria(serie).str.split(";").str[0].str.strip()


def agrupar_formato(serie: pd.Series) -> pd.Series:
    """Agrupa los formatos de edición en Tapa blanda, Tapa dura, Digital, Audio, Otro o Sin informar."""
    def grupo(valor: object) -> str:
        if pd.isna(valor):
            return "Sin informar"
        texto = str(valor).strip().lower()
        if texto in _FORMATOS_SIN_INFORMAR:
            return "Sin informar"
        for nombre, patrones in _PATRONES_FORMATO:
            if any(patron in texto for patron in patrones):
                return nombre
        return "Otro"

    return serie.map(grupo)


def rango_calificacion(serie: pd.Series) -> pd.Series:
    """Clasifica la calificación promedio en tres rangos de medio punto."""
    return pd.cut(
        serie,
        bins=[3.5, 4.0, 4.5, 5.0 + 1e-9],
        right=False,
        labels=ORDEN_RANGOS_CALIFICACION,
    ).astype("string")


def tasa_resenas(df: pd.DataFrame) -> pd.Series:
    """Proporción de calificaciones acompañadas de reseña escrita; nula si no hay calificaciones."""
    calificaciones = df["ratings_count"].where(df["ratings_count"].gt(0))
    return (df["reviews_count"] / calificaciones).round(4)


def marcar_registro_representativo(df: pd.DataFrame) -> pd.Series:
    """Marca una edición por obra (`work_id`): la de más calificaciones; en empate, el menor `book_id`.

    Las métricas de lectores se agregan a nivel de obra, así que sumarlas sobre todas las
    ediciones contaría dos veces a los mismos lectores.
    """
    orden = df.assign(_book_id_num=pd.to_numeric(df["book_id"], errors="coerce")).sort_values(
        ["work_id", "ratings_count", "_book_id_num"], ascending=[True, False, True]
    )
    representativos = orden.drop_duplicates(subset="work_id", keep="first").index
    return pd.Series(df.index.isin(representativos), index=df.index)


def sensibilidad_umbral(df: pd.DataFrame, umbrales: Iterable[int]) -> pd.DataFrame:
    """Compara cómo cambia el reparto de registros y obras entre áreas con distintos umbrales."""
    filas = []
    for umbral in umbrales:
        area = clasificar_extension(df["pages"], umbral)
        obras_en_ambas = df.assign(area=area).groupby("work_id")["area"].nunique().gt(1).sum()
        for nombre in ORDEN_AREAS:
            grupo = df.loc[area.eq(nombre)]
            filas.append({
                "umbral_paginas": umbral,
                "categoria_extension": nombre,
                "registros_edicion": len(grupo),
                "porcentaje_registros": round(len(grupo) / len(df) * 100, 2),
                "obras_unicas": grupo["work_id"].nunique(),
                "obras_con_ediciones_en_ambas_areas": int(obras_en_ambas),
            })
    return pd.DataFrame(filas)


def crear_ranking(df: pd.DataFrame, campo: str, top: int = 10) -> pd.DataFrame:
    """Top de valores de `campo` por área, con títulos, obras y calificación promedio.

    El porcentaje usa como denominador los registros del área con `campo` informado.
    """
    filas = []
    for area in ORDEN_AREAS:
        informados = df.loc[df["categoria_extension"].eq(area) & df[campo].notna()]
        resumen = (
            informados.groupby(campo)
            .agg(
                registros_edicion=("book_id", "size"),
                obras_unicas=("work_id", "nunique"),
                calificacion_promedio=("average_rating", "mean"),
                calificacion_mediana=("average_rating", "median"),
            )
            .sort_values(["registros_edicion", "obras_unicas"], ascending=False)
            .head(top)
        )
        for posicion, (valor, fila) in enumerate(resumen.iterrows(), start=1):
            filas.append({
                "categoria_extension": area,
                "posicion": posicion,
                campo: str(valor),
                "registros_edicion": int(fila["registros_edicion"]),
                "porcentaje_registros_con_valor": round(fila["registros_edicion"] / len(informados) * 100, 2),
                "obras_unicas": int(fila["obras_unicas"]),
                "calificacion_promedio": round(fila["calificacion_promedio"], 2),
                "calificacion_mediana": round(fila["calificacion_mediana"], 2),
            })
    return pd.DataFrame(filas)
