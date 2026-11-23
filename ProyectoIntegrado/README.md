# Proyecto Integrado III

Esta carpeta contiene el material vigente de Proyecto Integrado III dentro del
repositorio compartido. Machine Learning se conserva por separado en
`MachineLearning/RepoMachine_ProInteg3/`. Las dos materias conviven en la rama
`main`, pero sus actividades y dependencias no se mezclan.

## Proyecto Integrado III

El notebook `actividad1.ipynb` se conserva como parte del historial del
proyecto. Carga el
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

**Necesidad (escenario hipotético).** Una librería en Nueva York planea
organizar su exhibición en dos áreas: *Lecturas Ágiles* (libros delgados o
medianos) y *Grandes Clásicos y Sagas* (obras extensas). Para orientar el
espacio y revisar qué editoriales e idiomas considerar en compras importadas,
se caracteriza descriptivamente el catálogo de Goodreads con calificación
promedio ≥ 3.5. La diversidad de Nueva York hace relevante explorar idiomas,
pero el dataset no permite afirmar que su composición represente a la ciudad.

**Pregunta de análisis.** Entre los libros de Goodreads con calificación
promedio ≥ 3.5 y páginas válidas, ¿cómo se distribuyen por extensión, qué
editoriales e idiomas concentran más títulos en cada área y cómo varían las
calificaciones promedio?

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

**Ejecución.** Con el entorno instalado (ver *Entorno y ejecución*), desde la
carpeta `ProyectoIntegrado`:

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
- Se conservan `book_id` (edición), `work_id` (obra) y `first_author`; el
  DataFrame final tiene 235.104 filas y 20 columnas.

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

**Ejecución.** Con el entorno instalado (ver *Entorno y ejecución*), desde la
carpeta `ProyectoIntegrado`:

```powershell
jupyter nbconvert --to notebook --execute --inplace AE3/notebooks/AE3_transformacion_enriquecimiento.ipynb
```

El notebook crea `AE3/resultados/` si no existe y regenera en cada ejecución el
dataset preparado, las tablas `.csv` y `resumen_dataframe_final.txt` (UTF-8,
rutas relativas). Después vuelve a leer los archivos y compara sus dimensiones
con las tablas en memoria; esta comprobación no compara todos sus valores.

## AE4: Dashboard de Goodreads

Aplicación descriptiva interactiva construida con Streamlit y Plotly a partir
del dataset preparado y las tablas de AE3. Sus análisis comparan extensión,
editoriales, idiomas y calificaciones usando título, primer autor, páginas,
calificación promedio, editorial e idioma. Los rankings principales cuentan
obras únicas; el filtro de formato solo ayuda a preparar una lista auxiliar de
candidatos y no cambia los análisis. No crea datos sintéticos ni estima ventas.

Desde la carpeta `ProyectoIntegrado`, ejecuta:

```powershell
streamlit run AE4/app.py
```

La página se abre localmente en el navegador, normalmente en
`http://localhost:8501`. Requiere que AE3 haya generado
`AE3/resultados/libros_preparados_enriquecidos.csv` y
`AE3/resultados/t1_control_poblacion.csv`,
`AE3/resultados/t2b_sensibilidad_umbral.csv`. La composición por idioma se
calcula sobre la selección actual. La guía y las pruebas están en
`AE4/README.md` y `AE4/test_dashboard.py`.

**Publicación:** todavía no hay una URL pública. Streamlit Community Cloud
genera una dirección `https://<subdominio>.streamlit.app` al conectar el
repositorio, la rama y `ProyectoIntegrado/AE4/app.py`. La aplicación debe
publicarse desde el repositorio de entrega y necesita los archivos de AE3.
Cuando exista, añade aquí la URL real; no uses `localhost` como enlace público.
Los pasos están en `AE4/README.md`, sección *Publicación web*.

**Documento final y presentación.**

```text
AE4/documento/Proyecto_Integrado_Goodreads_documento_final.pdf    Documento completo del proyecto (AE2, AE3 y AE4)
AE4/documento/Proyecto_Integrado_Goodreads_documento_final.docx   Fuente editable del documento
AE4/documento/generar_figuras.py                                  Genera las figuras y cifras del documento
AE4/documento/figuras/                                            Figuras PNG y cifras_documento.json
AE4/documento/capturas/                                           Capturas de la aplicación (anexo A)
AE4/presentacion/guion_presentacion.md                            Guion de la presentación de 10 minutos
```

El documento integra portada, contenido e índices, introducción, necesidad,
justificación, objetivos, marco teórico, metodología, transformación y
enriquecimiento (AE3), métricas y visualizaciones (sección 10), resultados,
conclusiones y recomendaciones, y referencias. Sus cifras se calculan con las
mismas funciones de `AE4/dashboard.py` que usa la aplicación. Para regenerar
las figuras, desde la carpeta `ProyectoIntegrado`:

```powershell
python AE4/documento/generar_figuras.py
```

## Estructura

```text
actividad1.ipynb                 Notebook conservado del proyecto
AE2/                             Etapa 1 del proyecto integrador (necesidad analítica)
AE3/                             Etapa 2 del proyecto integrador (transformación y enriquecimiento)
AE4/                             Dashboard descriptivo de Goodreads (Streamlit y Plotly)
AE4/documento/                   Documento final del proyecto (PDF y Word) y sus figuras
AE4/presentacion/                Guion de la presentación
src/hf_loader.py                 Carga de datasets de Hugging Face
src/preparacion.py               Transformación y enriquecimiento (AE3)
src/reportes.py                  Generacion de reportes
reportes/goodreads_books.txt     Reporte generado por la actividad
requirements.txt                 Dependencias del proyecto
```

## Entorno y ejecución

En Windows PowerShell, desde la raíz del workspace:

```powershell
Set-Location ProyectoIntegrado
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
jupyter notebook actividad1.ipynb
```

Para ejecutar AE2 o AE3, abre el notebook correspondiente desde esta carpeta o
usa `jupyter nbconvert --to notebook --execute --inplace` con su ruta indicada
arriba. La primera carga de Goodreads requiere conexión a internet.

El workflow de GitHub Actions está en
`.github/workflows/proyecto-integrado-actividad1.yml`, en la raíz del
workspace. Se activa al hacer push a `main`, ejecuta el notebook
`actividad1.ipynb` y actualiza su reporte. AE2 y AE3 se ejecutan desde sus
notebooks y no forman parte de ese workflow.
