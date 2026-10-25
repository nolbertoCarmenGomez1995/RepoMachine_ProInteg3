# RepoMachine_ProInteg3

Repositorio de trabajo para Proyecto Integrado III y Machine Learning.

## Proyecto Integrado III

La actividad propia de este repositorio esta en `actividad1.ipynb`. Carga el
dataset `pfaha/goodreads-books` desde Hugging Face, selecciona y transforma
columnas de libros, limpia valores nulos, filtra por calificacion y guarda un
reporte en `reportes/goodreads_books.txt`.

El notebook utiliza `HFDatasetLoader` y `Reportes`, implementados en
`src/hf_loader.py` y `src/reportes.py`.

## Machine Learning

`src/regresion_lineal.py` y `src/clasificador_text.py` contienen las clases de
regresion y clasificacion. La carpeta `sincronicas/` conserva los notebooks de
las sesiones del curso, cuyos ejemplos usan datasets distintos al de libros.

Esos notebooks hacen imports desde `clases_po`, una carpeta que no existe en
esta estructura. Se conservan como material de referencia y requieren adaptar
sus imports y, segun el ejercicio, sus datos o la interfaz de las clases antes
de ejecutarse con este proyecto.

`sincronicas/Semana_3_LIBROS.ipynb` adapta el análisis de la semana 3 a Goodreads:
explora el dataset, deriva categorías de calificación para clasificación de
texto y estima la calificación con regresión lineal.

El notebook documenta el preprocesamiento, compara Naive Bayes y regresión
logística para clasificar categorías derivadas de la calificación y entrena una
regresión lineal para estimar la calificación desde las páginas. Al terminar
genera `reportes/resumen_modelos_libros.txt` con los resultados de esa ejecución.
Las categorías de clasificación son cortes didácticos de la calificación; no
son etiquetas originales del dataset.

## Estructura

```text
actividad1.ipynb                 Actividad propia con Goodreads
sincronicas/Semana_3_LIBROS.ipynb Semana 3 adaptada al dataset de libros
src/hf_loader.py                 Carga de datasets de Hugging Face
src/reportes.py                  Generacion de reportes
src/regresion_lineal.py          Clase de regresion lineal
src/clasificador_text.py         Clase de clasificacion de texto
sincronicas/                     Material de las sesiones del curso
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

Para ejecutar la actividad de Machine Learning y generar el resumen de los
modelos:

```powershell
jupyter notebook sincronicas/Semana_3_LIBROS.ipynb
```

Ejecuta todas las celdas en orden. El resumen se genera automáticamente en
`reportes/resumen_modelos_libros.txt`; contiene las métricas de la ejecución,
no valores escritos manualmente. Los archivos pickle de los modelos se guardan
temporalmente y se eliminan al terminar; así cada ejecución genera solo el
resumen y no acumula copias de modelos.

La carga de Goodreads requiere conexion a internet. El workflow de GitHub
Actions ejecuta `actividad1.ipynb` al hacer push a `main` y actualiza el
reporte generado. El flujo de Machine Learning está separado en
`.github/workflows/ejecutar-semana-3-libros.yml`: se activa al hacer push a
`main`, ejecuta el notebook completo y publica el resumen `.txt` y el notebook
ejecutado como artefacto descargable en la ejecución de GitHub Actions. El
workflow de Semana 1 se conserva como ejemplo del profesor.