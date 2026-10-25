# RepoMachine_ProInteg3

Repositorio de trabajo para Proyecto Integrado III. Esta rama (`EA2_Proyecto`)
contiene solo el material del proyecto integrador; el material de Machine
Learning se conserva en la rama `main`.

## Proyecto Integrado III

La actividad propia de este repositorio esta en `actividad1.ipynb`. Carga el
dataset `pfaha/goodreads-books` desde Hugging Face, selecciona y transforma
columnas de libros, limpia valores nulos, filtra por calificacion y guarda un
reporte en `reportes/goodreads_books.txt`.

El notebook utiliza `HFDatasetLoader` y `Reportes`, implementados en
`src/hf_loader.py` y `src/reportes.py`.

## AE2: Necesidad analítica

Primera etapa del proyecto integrador: definir y documentar una necesidad de
analítica descriptiva a partir de un dataset de Hugging Face.

**Propósito.** Obtener el dataset mediante código, reconocer su contenido
(registros, dimensiones, columnas, tipos y nulos) y generar automáticamente un
resumen del DataFrame en `.txt`, como apoyo para formular la necesidad y
diseñar el proyecto.

**Necesidad (escenario hipotético).** Una librería planea rediseñar su
exhibición en dos áreas: *Lecturas Ágiles* (libros delgados o medianos) y
*Grandes Clásicos y Sagas* (obras extensas). Para decidir qué porcentaje de
espacio asignar a cada área y qué editoriales e idiomas priorizar en sus
compras importadas, necesita un diagnóstico descriptivo de los libros
destacados (calificación promedio ≥ 3.5) en Goodreads.

**Pregunta de análisis.** Entre los libros de Goodreads con calificación
promedio ≥ 3.5, ¿cómo se distribuyen según su extensión en páginas y qué
editoriales e idiomas concentran más títulos, calificaciones y reseñas en cada
grupo?

**Dataset.**

| Campo | Valor |
|---|---|
| Nombre | Goodreads Books Metadata |
| Identificador | `pfaha/goodreads-books` |
| Enlace | https://huggingface.co/datasets/pfaha/goodreads-books |
| Configuración / split | `default` / `train` (completo, sin muestreo) |
| Revisión | `43b3198cd7ec9c142d56181f1a09ed9e8c112610` |
| Fecha de consulta | 2026-10-24 |
| Tamaño | 500.000 filas y 24 columnas |

El dataset sigue creciendo, por eso el notebook fija la revisión consultada.
Los datos son reales (scraping de páginas públicas de Goodreads), no
sintéticos. Su licencia figura como `other`: se usan con fines educativos y
respetando los [Términos de Servicio de Goodreads](https://www.goodreads.com/about/terms).
Los datos **no se guardan en el repositorio**: se descargan al ejecutar el
notebook, de forma pública y sin token, y quedan en la caché local de Hugging
Face.

**Archivos de AE2.**

```text
AE2/documento/AE2_necesidad_analitica_goodreads.docx   Documento de la necesidad y el diseño
AE2/notebooks/AE2_exploracion_goodreads.ipynb          Obtención y exploración del dataset
AE2/resultados/resumen_dataframe.txt                   Resumen generado por el notebook
```

**Ejecución.** Con el entorno instalado (ver *Entorno y ejecucion*), desde la
raíz del repositorio:

```powershell
jupyter notebook AE2/notebooks/AE2_exploracion_goodreads.ipynb
```

Ejecuta todas las celdas en orden, o sin abrir Jupyter:

```powershell
jupyter nbconvert --to notebook --execute --inplace AE2/notebooks/AE2_exploracion_goodreads.ipynb
```

La primera ejecución descarga unos 180 MB y requiere conexión a internet. El
notebook crea `AE2/resultados/` si no existe y regenera
`resumen_dataframe.txt` (UTF-8) en cada ejecución.

## Estructura

```text
actividad1.ipynb                 Actividad propia con Goodreads
AE2/                             Etapa 1 del proyecto integrador (necesidad analítica)
src/hf_loader.py                 Carga de datasets de Hugging Face
src/reportes.py                  Generacion de reportes
reportes/goodreads_books.txt     Reporte generado por la actividad
requirements.txt                 Dependencias del proyecto
```

## Entorno y ejecucion

Desde la raiz del repositorio, en Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook actividad1.ipynb
```

La carga de Goodreads requiere conexion a internet. El workflow de GitHub
Actions ejecuta `actividad1.ipynb` al hacer push a `main` y actualiza el
reporte generado.
