# AE4: Dashboard descriptivo de Goodreads

La aplicación presenta los resultados de AE3 como una página interactiva local
con Streamlit y gráficas Plotly. Permite comparar las dos áreas y obtener una
lista de títulos que sí coincide con los filtros de exhibición; no genera datos
sintéticos ni predicciones de ventas.

## Ejecutar

Desde la carpeta `ProyectoIntegrado`, instala las dependencias del proyecto si
aún no están instaladas y ejecuta:

```powershell
python -m pip install -r requirements.txt
streamlit run AE4/app.py
```

Streamlit abrirá la aplicación en el navegador, normalmente en
`http://localhost:8501`. La aplicación necesita los resultados generados por
AE3 en `AE3/resultados/`.

Para una instalación mínima de la aplicación:

```powershell
python -m pip install -r AE4/requirements.txt
```

## Validar

Desde la carpeta `ProyectoIntegrado`:

```powershell
python -m unittest discover -s AE4 -p "test_*.py"
```

Las pruebas comparan el reparto por área, los rankings de editoriales e idiomas
y las estadísticas de calificación; también verifican filtros combinados y que
la lista de candidatos tenga una obra única con una edición coincidente.

## Interpretación

- La población base ya está filtrada en AE3: calificación promedio de 3,5 o más
  y páginas válidas entre 1 y 5.000.
- Los criterios distintos se combinan con **Y**; varias opciones dentro de un
  mismo filtro se combinan con **O**. Dejar un selector vacío significa incluir
  todos sus valores. La búsqueda de editorial es parcial y no distingue
  mayúsculas. Una selección que no coincide muestra cero resultados.
- Los análisis principales usan título, primer autor, páginas, calificación
  promedio, editorial e idioma. El área de extensión se deriva de las páginas.
- P2 cuenta obras únicas (`work_id`) y las asigna al área mediante una edición
  coincidente con los filtros; muestra además el número de ediciones.
- P3 y P4 presentan los diez valores principales por número de obras únicas y
  muestran cantidad de títulos y calificación promedio. P5 compara media,
  desviación estándar, cuartiles e intervalo intercuartil.
- La composición por idioma incluye ediciones sin idioma informado. Sus
  porcentajes se calculan sobre las ediciones del área; las obras pueden tener
  ediciones en más de un idioma.
- La lista de candidatos agrupa por `work_id`, muestra una edición que sí pasó
  los filtros y ordena por calificación promedio. Formato solo filtra esta
  lista; no altera los gráficos ni las respuestas P1–P6. La lista ayuda a revisar
  títulos, no es una recomendación automática de compra.
- La población y sus exclusiones, la sensibilidad global al umbral de páginas y
  los hallazgos de AE3 son referencias globales; no cambian con los filtros.
- `book_id` identifica una edición y `work_id` identifica una obra.
- Los datos describen Goodreads, no ventas, inventario ni demanda comprobada
  de una librería.
- La ubicación de la librería en Nueva York es hipotética. La fuente no registra
  la ciudad de sus usuarios; la composición por idioma no estima el mercado local.
- La fuente no tiene una variable de fecha para mostrar un periodo temporal.

## Publicación web

La aplicación todavía no está desplegada públicamente. Streamlit Community
Cloud puede conectarse al repositorio de GitHub y publicar la aplicación en una
dirección `https://<subdominio>.streamlit.app`. Al crearla, se seleccionan el
repositorio, la rama y el archivo principal `ProyectoIntegrado/AE4/app.py`;
`AE4/requirements.txt` declara las dependencias de la aplicación.

El despliegue debe hacerse cuando el código y los archivos necesarios de AE3
estén en el repositorio de entrega: el CSV preparado, `t1_control_poblacion.csv`
y `t2b_sensibilidad_umbral.csv`. La composición por idioma se calcula desde el
CSV filtrado y no requiere `t6_composicion_idioma.csv`. El CSV preparado
pesa aproximadamente 48 MB. Después se debe copiar la URL real aquí y en el
README del proyecto. No se debe compartir una URL inventada o una dirección
local `localhost`.

Pasos para publicarla (los hace una cuenta de GitHub con acceso al
repositorio, por ejemplo la del dueño):

1. Entrar a https://share.streamlit.io e iniciar sesión con GitHub.
2. Elegir **Create app** → **Deploy a public app from GitHub**.
3. Completar: repositorio `nolbertoCarmenGomez1995/RepoMachine_ProInteg3`,
   rama `main` y archivo principal `ProyectoIntegrado/AE4/app.py`.
4. En **Advanced settings**, elegir Python 3.13, la versión con la que se
   probaron la aplicación y sus pruebas.
5. Pulsar **Deploy** y esperar a que termine la instalación de
   `AE4/requirements.txt`.
6. Copiar la URL `https://….streamlit.app` en este README y en
   `ProyectoIntegrado/README.md`, y compartirla en la entrega.

Guía oficial: [desplegar en Streamlit Community Cloud](https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy).

## Documento final

El documento completo del proyecto está en
`AE4/documento/Proyecto_Integrado_Goodreads_documento_final.pdf` (con su
versión editable `.docx`). Su sección 10 presenta las métricas y los gráficos
de cada pregunta con las mismas cifras de la aplicación sin filtros; las figuras
se regeneran con `python AE4/documento/generar_figuras.py` desde la carpeta
`ProyectoIntegrado`.
