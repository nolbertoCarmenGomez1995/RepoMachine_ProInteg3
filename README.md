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

## AE3: Transformación y enriquecimiento

Segunda etapa del proyecto integrador: transformar y enriquecer el dataset de
AE2 para responder descriptivamente las preguntas de negocio, con una tabla por
pregunta, y dejar los resultados listos para la visualización de AE4. Parte del
mismo dataset y revisión de AE2 (`pfaha/goodreads-books`, split `train`
completo, revisión `43b3198`).

**Transformaciones y reglas de calidad.**

- Población: calificación promedio ≥ 3,5 y páginas entre 1 y 5.000. Se
  excluyen y se cuentan aparte los registros sin calificación, sin páginas,
  con 0 páginas o con más de 5.000.
- Se conservan los registros sin editorial, idioma o formato, y se reporta
  cuántos faltan.
- Editorial e idioma: se quitan los espacios externos y los textos vacíos pasan
  a nulo. Los valores originales se conservan (`publisher_original`,
  `language_original`).
- Se conservan `book_id` (edición) y `work_id` (obra); el DataFrame final
  tiene 235.104 filas y 19 columnas.

**Variables incorporadas.**

| Variable | Regla |
|---|---|
| `categoria_extension` | ≤ 350 páginas → Lecturas Ágiles; > 350 → Obras extensas |
| `rango_calificacion` | 3,5 a 3,99 / 4,0 a 4,49 / 4,5 a 5,0 |
| `idioma_normalizado` | Primer nombre de la etiqueta ("Spanish; Castilian" → "Spanish") |
| `cantidad_series` | Número de series listadas en `series` |
| `formato_grupo` | Tapa blanda, Tapa dura, Digital, Audio, Otro o Sin informar |
| `tasa_resenas` | `reviews_count / ratings_count` |
| `registro_representativo_obra` | Una edición por obra (la de más calificaciones), para sumar métricas de lectores sin doble conteo |

**Preguntas de negocio y tablas.**

| Pregunta | Archivo |
|---|---|
| P1. Población de estudio y exclusiones por criterio | `t1_control_poblacion.csv` |
| P2. Número y porcentaje de títulos por área; sensibilidad del umbral | `t2_reparto_por_extension.csv`, `t2b_sensibilidad_umbral.csv` |
| P3. Diez editoriales con más títulos por área y su calificación promedio | `t3_top_editoriales.csv` |
| P4. Diez idiomas con más títulos por área y su calificación promedio | `t4_top_idiomas.csv` |
| P5. Distribución de la calificación promedio por área | `t5_calificacion_por_extension.csv` |
| P6. Composición por idioma de cada área | `t6_composicion_idioma.csv` |
| Complementaria. Participación de lectores, series y formato por área | `t7_participacion_series.csv`, `t8_formato_por_extension.csv` |

**Archivos de AE3.**

```text
AE3/documento/AE3_transformacion_enriquecimiento_goodreads.docx   Documento actualizado
AE3/notebooks/AE3_transformacion_enriquecimiento.ipynb            Transformación, enriquecimiento y respuestas
AE3/resultados/libros_preparados_enriquecidos.csv                 Dataset preparado y enriquecido
AE3/resultados/t1_...csv a t8_...csv                              Tablas de resultados
AE3/resultados/resumen_dataframe_final.txt                        Resumen descriptivo del DataFrame final
src/preparacion.py                                                Funciones de transformación y enriquecimiento
```

**Ejecución.** Con el entorno instalado (ver *Entorno y ejecucion*), desde la
raíz del repositorio:

```powershell
jupyter nbconvert --to notebook --execute --inplace AE3/notebooks/AE3_transformacion_enriquecimiento.ipynb
```

El notebook crea `AE3/resultados/` si no existe y regenera en cada ejecución el
dataset preparado, las tablas `.csv` y `resumen_dataframe_final.txt` (UTF-8,
rutas relativas). Después vuelve a leer los archivos para verificar que
coinciden con el notebook.

## Estructura

```text
actividad1.ipynb                 Actividad propia con Goodreads
AE2/                             Etapa 1 del proyecto integrador (necesidad analítica)
AE3/                             Etapa 2 del proyecto integrador (transformación y enriquecimiento)
src/hf_loader.py                 Carga de datasets de Hugging Face
src/preparacion.py               Transformación y enriquecimiento (AE3)
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
