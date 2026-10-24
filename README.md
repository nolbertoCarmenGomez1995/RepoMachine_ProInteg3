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

## Estructura

```text
actividad1.ipynb                 Actividad propia con Goodreads
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

La carga de Goodreads requiere conexion a internet. El workflow de GitHub
Actions ejecuta `actividad1.ipynb` al hacer push a `main` y actualiza el
reporte generado.