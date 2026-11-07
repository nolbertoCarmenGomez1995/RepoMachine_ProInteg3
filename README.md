# RepoMachine_ProInteg3

## Actividad 3 — Segmentación de libros con Goodreads

### Pregunta de negocio

Entre los libros de Goodreads con calificación promedio igual o superior a
3,5, ¿qué perfiles de extensión física y participación de lectores se pueden
identificar para orientar cómo una librería distribuye su espacio de exhibición
y prioriza su curaduría?

El beneficiario propuesto es el equipo de compras y exhibición de **Librerías
Plaza Lectura**. La decisión que se busca apoyar es definir perfiles de catálogo
y usarlos como referencia inicial para organizar la exhibición. Es un escenario
académico hipotético: el dataset representa Goodreads, no inventarios ni ventas
de esa librería.

### Dataset y construcción del DataFrame

- **Dataset:** [`pfaha/goodreads-books`](https://huggingface.co/datasets/pfaha/goodreads-books), split `train`.

- **Unidad de análisis:** un registro bibliográfico.
- **Carga automática:** `HFDatasetLoader` obtiene los datos desde Hugging Face y construye el DataFrame; no se requiere descargar archivos manualmente.
- El programa informa dimensiones, columnas, tipos, una muestra y una auditoría de calidad antes del modelado.

### Modelo único de la entrega: K-Means

La Actividad 3 utiliza **un modelo: K-Means**, de aprendizaje no supervisado.
No se dispone de una etiqueta que identifique de antemano el tipo comercial
de cada libro; por eso se agrupan registros según similitud en páginas,
calificación y participación de lectores.

El algoritmo comienza con `k` centroides, asigna cada libro al centroide más
cercano en el espacio de variables estandarizadas, recalcula los centroides
como promedios de los grupos y repite asignación y actualización hasta
converger. Se prueban `k=2, 3, 4, 5, 6`; se selecciona el valor con mayor
silhouette en un conjunto de validación separado de la muestra de ajuste.

Variables que determinan los grupos:

- `paginas`: extensión física.
- `calificacion`: promedio de lectores.
- `log1p_cantidad_calificaciones` y `log1p_cantidad_resenas`: participación,
  comprimida con `log1p` para reducir la influencia de valores extremos.

La imputación por mediana y el escalado estándar se ajustan solo con la muestra
de entrenamiento; luego se aplican al conjunto de validación y a los libros
que se perfilan. K-Means se ejecuta con `n_init=10` y semilla `42`. La
selección usa silhouette y Davies–Bouldin; también se informa la inercia.
Silhouette compara cohesión y separación entre grupos; Davies–Bouldin es
mejor cuando es menor, y la inercia mide distancias internas, aunque tiende a
bajar al aumentar `k`.

**Ventajas:** los segmentos son interpretables y pueden resumirse por tamaño,
páginas, ratings, reseñas, editoriales e idiomas. **Limitaciones:** K-Means
depende de la escala, las variables, los filtros, el muestreo y la semilla;
requiere elegir `k` y puede favorecer grupos compactos. Los segmentos no
demuestran causas, demanda, ventas ni el espacio físico que necesita cada
libro. La proporción de títulos sirve solo como referencia para discutir la
curaduría y debe contrastarse con el inventario y las ventas de la librería.

### Preprocesamiento y evidencias

El script `src/actividad3_goodreads.py` registra las filas iniciales y
resultantes, duplicados removidos, faltantes, inválidos de páginas, cuartiles
y valla IQR. Para el análisis se consideran calificaciones `[3.5, 5.0]`,
páginas de al menos 20 y hasta la valla superior `Q3 + 1.5 × IQR`; los
conteos negativos o inválidos pasan a faltantes y se imputan dentro del
pipeline. Se eliminan solo duplicados de título, autor y variables usadas en
el análisis. Los filtros responden al escenario de libros destacados y a la
escala física; por eso los resultados no representan todo Goodreads.

### Ejecución y archivos generados

Desde la raíz del repositorio:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m src.actividad3_goodreads
```

La ejecución genera:

- `reportes/actividad3_goodreads.txt`: resumen automático con pregunta,
  dataset, preprocesamiento, configuración, fecha y métricas.
- `reportes/hallazgos_actividad3.md`: interpretación y recomendación generadas
  localmente con los resultados de esa ejecución. Está excluido de Git; en
  GitHub se incluye como parte del artefacto de Actions.
- `reportes/figuras/`: curva silhouette y visualización de los segmentos,
  enlazadas desde el documento de hallazgos.
- `modelos/libros/kmeans_actividad3_goodreads.joblib`: pipeline entrenado;
  esta carpeta está excluida de Git.

El workflow
`.github/workflows/ejecutar-actividad3-goodreads.yml` se activa en cada `push` a
`main`. Ejecuta pruebas, descarga el dataset, prepara datos, evalúa y ajusta
un K-Means y publica resumen, hallazgos, gráficas y modelo como artefacto.
Actualiza en `main` el `.txt` y las gráficas; el `.md` se entrega dentro del
artefacto, pero no se versiona en el repositorio. Para la entrega
de Canvas aún se debe enlazar una ejecución exitosa de Actions y confirmar que
el docente pueda acceder al repositorio.

Repositorio de trabajo para Proyecto Integrado III y Machine Learning.

## Proyecto Integrado III

La actividad propia de este repositorio esta en `actividad1.ipynb`. Carga el
dataset `pfaha/goodreads-books` desde Hugging Face, selecciona y transforma
columnas de libros, filtra calificaciones y guarda reportes en `reportes/`.
La auditoria de calidad conserva y señala los faltantes de campos opcionales
en vez de descartar esas filas.

El notebook utiliza `HFDatasetLoader` y `Reportes`, implementados en
`src/hf_loader.py` y `src/reportes.py`.

## Machine Learning

`src/regresion_lineal.py` y `src/clasificador_text.py` contienen las clases de
regresion y clasificacion. Los notebooks `Semana_1SINC.ipynb`,
`Semana_2SINC.ipynb` y `Semana_3SINC.ipynb` conservan los ejemplos originales
del curso; usan otros datasets e imports desde `clases_po`, que no existe en
esta estructura, por lo que se mantienen como referencia.

`sincronicas/Semana_3_LIBROS.ipynb` adapta el análisis de la semana 3 a Goodreads:
explora el dataset, deriva categorías de calificación para clasificación de
texto y estima la calificación con regresión lineal.

El notebook documenta el preprocesamiento, compara Naive Bayes y regresión
logística para clasificar categorías derivadas de la calificación y entrena una
regresión lineal para estimar la calificación desde las páginas. El resumen
`reportes/resumen_modelos_libros.txt` corresponde a ese ejercicio de práctica,
no a la Actividad 3.
Las categorías de clasificación son cortes didácticos de la calificación; no
son etiquetas originales del dataset.

Los notebooks `Semana_3_LIBROS.ipynb`, `Semana_4_LIBROS.ipynb` y
`Semana_5_LIBROS.ipynb` son ejercicios de práctica. Comparan distintos modelos
y no forman parte del flujo de entrega de la Actividad 3; su workflow ejecuta
únicamente el K-Means descrito arriba.

La preparación compartida y la auditoría están en `src/goodreads.py`. La
auditoría informa faltantes, duplicados y páginas atípicas sin eliminarlas
globalmente; cada modelo aplica sus propios filtros. Las reglas se verifican
con `python -m unittest discover -s tests -v`.

## Estructura

```text
actividad1.ipynb                 Actividad propia con Goodreads
sincronicas/Semana_3_LIBROS.ipynb Práctica de clasificación y regresión
sincronicas/Semana_4_LIBROS.ipynb Semana 4: clasificación tabular
sincronicas/Semana_5_LIBROS.ipynb Semana 5: agrupamiento K-Means
src/actividad3_goodreads.py      Flujo reproducible de la Actividad 3
src/hf_loader.py                 Carga de datasets de Hugging Face
src/goodreads.py                 Preparación y auditoría de Goodreads
src/reportes.py                  Generacion de reportes
src/regresion_lineal.py          Clase de regresion lineal
src/clasificador_text.py         Clase de clasificacion de texto
sincronicas/                     Material de las sesiones del curso
reportes/goodreads_books.txt     Reporte generado por la actividad
reportes/actividad3_goodreads.txt Resumen final de la Actividad 3
reportes/hallazgos_actividad3.md Hallazgos locales (ignorado por Git)
tests/                           Pruebas de preparación y auditoría
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

Para ejecutar manualmente la Actividad 3 y generar el resumen:

```powershell
python -m src.actividad3_goodreads
```

La carga de Goodreads requiere internet. El workflow de Actividad 3 se activa
al hacer `push` a `main`, ejecuta las pruebas y el flujo de K-Means, y publica
resumen, hallazgos, gráficas y modelo como artefacto descargable. En `main`
actualiza el resumen y el documento de hallazgos generados automáticamente.