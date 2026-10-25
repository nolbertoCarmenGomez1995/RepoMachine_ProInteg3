from __future__ import annotations

from pathlib import Path
import pandas as pd


class Reportes:

    def generar_reporte(self, df: pd.DataFrame) -> str:
        """Genera el contenido textual del reporte."""
        self._validar_dataframe(df)
        numericas = df.select_dtypes(include="number")
        lineas = [
            "REPORTE DEL DATAFRAME TRANSFORMADO",
            "=" * 60,
            f"Filas: {len(df)}",
            f"Columnas: {len(df.columns)}",
            f"Duplicados: {int(df.duplicated().sum())}",
            "",
            "Columnas y tipos:",
            *[f"- {columna}: {tipo}" for columna, tipo in df.dtypes.items()],
            "",
            "Valores nulos por columna:",
            *[f"- {columna}: {cantidad}" for columna, cantidad in df.isna().sum().items()],
        ]

        if not numericas.empty:
            lineas += [
                "",
                "Estadísticas numéricas:",
                numericas.describe().round(3).to_string(),
            ]

        return "\n".join(lineas) + "\n"

    def imprimir_reporte(self, df: pd.DataFrame) -> None:
        """Imprime en la consola el reporte del DataFrame."""
        print(self.generar_reporte(df), end="")

    def guardar_reporte(self, df: pd.DataFrame, ruta: str | Path) -> Path:
        """Guarda el reporte en un archivo de texto y devuelve su ruta."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_reporte(df), encoding="utf-8")
        return path

    def generar_resumen_dataframe(self, df: pd.DataFrame, metadatos: dict[str, object]) -> str:
        """Genera el resumen del DataFrame obtenido, encabezado con los metadatos de su origen."""
        self._validar_dataframe(df)
        nulos = df.isna().sum()
        lineas = [
            "RESUMEN DEL DATAFRAME",
            "=" * 60,
            *[f"{clave}: {valor}" for clave, valor in metadatos.items()],
            "",
            f"Filas: {len(df)}",
            f"Columnas: {len(df.columns)}",
            "",
            "Columnas y tipos:",
            *[f"- {columna}: {tipo}" for columna, tipo in df.dtypes.items()],
            "",
            "Valores nulos por columna:",
            *[f"- {columna}: {int(cantidad)}" for columna, cantidad in nulos.items()],
            "",
            "Valores vacíos por columna (texto '' o lista vacía, no cuentan como nulos):",
            *[f"- {columna}: {self._contar_vacios(df[columna])}" for columna in df.columns],
        ]
        return "\n".join(lineas) + "\n"

    def guardar_resumen_dataframe(
        self, df: pd.DataFrame, ruta: str | Path, metadatos: dict[str, object]
    ) -> Path:
        """Guarda el resumen del DataFrame en un archivo de texto UTF-8 y devuelve su ruta."""
        path = Path(ruta)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(self.generar_resumen_dataframe(df, metadatos), encoding="utf-8")
        return path

    @staticmethod
    def _contar_vacios(serie: pd.Series) -> int:
        def es_vacio(valor: object) -> bool:
            if isinstance(valor, str):
                return valor.strip() == ""
            if hasattr(valor, "__len__"):
                return len(valor) == 0
            return False

        return int(serie.dropna().map(es_vacio).sum())

    @staticmethod
    def _validar_dataframe(df: pd.DataFrame) -> None:
        if not isinstance(df, pd.DataFrame):
            raise TypeError("df debe ser un pandas.DataFrame.")