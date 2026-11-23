# Guion de la presentación (10 minutos)

Proyecto integrador: diagnóstico descriptivo de libros destacados de Goodreads
para el rediseño de la exhibición de una librería (escenario hipotético en
Nueva York).

| Tiempo | Bloque | Presenta |
|---|---|---|
| 0:00 – 2:00 | Necesidad, preguntas y datos | Andrés |
| 2:00 – 5:00 | Demostración: P1, P2 y resumen | Andrés |
| 5:00 – 8:00 | Demostración: P3, P4, P6 y P5 | Nolberto |
| 8:00 – 10:00 | Conclusiones, recomendaciones y limitaciones | Nolberto |

El reparto es una sugerencia: pueden intercambiar bloques, pero cada
integrante debe explicar una parte y su relación con la necesidad.

Todas las cifras corresponden a la aplicación **sin filtros** (así se abre).

## 0:00 – 2:00 · Necesidad, preguntas y datos (Andrés)

Abrir la aplicación y desplegar *Necesidad, preguntas de negocio y dataset*.

- **Necesidad.** Una librería en Nueva York (escenario hipotético) quiere
  repartir su espacio entre *Lecturas Ágiles* y *Grandes Clásicos y Sagas*, y
  decidir qué editoriales e idiomas priorizar en sus compras importadas.
- **Pregunta.** Entre los libros de Goodreads con calificación ≥ 3,5, ¿cómo se
  distribuyen por extensión, qué editoriales e idiomas concentran más títulos y
  cómo varía la calificación?
- **Datos.** `pfaha/goodreads-books` de Hugging Face: 500.000 registros y
  24 columnas, con la revisión fijada. En AE3 se limpiaron y enriquecieron;
  quedan 235.104 ediciones de 211.975 obras.
- Señalar los cuatro indicadores de arriba: 235.104 registros, 211.975 títulos
  únicos, calificación media 4,07 y mediana de 240 páginas.

## 2:00 – 5:00 · Demostración P1, P2 y resumen (Andrés)

1. **Pestaña Población y método (P1).**
   - **Métrica:** ediciones excluidas por criterio.
   - **Cifra:** de 500.000 quedan 235.104 (47,02 %). El mayor recorte es la
     calificación < 3,5 (223.590); entre los destacados, faltan páginas en 22.129.
   - **Mensaje:** "sabemos exactamente sobre qué libros respondemos".
2. **Pestaña Extensión (P2).**
   - **Métrica:** títulos únicos por área y su porcentaje.
   - **Cifra:** Lecturas Ágiles 161.020 (75,96 %) y Obras extensas 50.955 (24,04 %).
   - Mostrar el gráfico de sensibilidad: con 250 páginas sería 52 % / 48 %; con
     400, 83 % / 17 %. El umbral de 350 está cerca del percentil 75.
   - **Decisión:** punto de partida de ¾ y ¼ de títulos.
   - **Limitación:** el porcentaje de títulos no es porcentaje de estante.
3. **Pestaña Resumen para decidir.** Mostrar que todo se recalcula con los
   filtros: por ejemplo, elegir el idioma *Spanish* en la barra lateral y volver
   a quitarlo.

## 5:00 – 8:00 · Demostración P3, P4, P6 y P5 (Nolberto)

1. **Pestaña Editoriales (P3).**
   - **Métrica:** títulos únicos por editorial y su calificación promedio.
   - **Cifra:** Routledge lidera Lecturas Ágiles (2.246 títulos; 4,09) y Oxford
     University Press lidera Obras extensas (1.095; 4,10).
   - **Mensaje:** el catálogo es muy fragmentado, porque la primera editorial
     tiene apenas un 2 % de su área.
   - **Limitación:** más títulos no significa más ventas.
2. **Pestaña Idiomas (P4 y P6).**
   - **Cifra:** el inglés domina, con 139.094 títulos en Lecturas Ágiles y 43.894
     en Obras extensas.
   - **En P6:** el inglés es el 84 % y el 81 % de las ediciones. El francés y el
     alemán pesan más en Obras extensas (3,4 % y 3,6 %).
   - **Decisión:** priorizar el inglés y explorar francés y alemán en obras extensas.
   - **Limitación:** Goodreads no registra la ciudad de sus usuarios, así que no
     representa a Nueva York.
3. **Pestaña Calificaciones (P5).**
   - **Cifra:** media de 4,07 frente a 4,08, con la misma mediana (4,00).
   - **Mensaje:** la calificación no distingue las áreas, por lo que no sirve
     para repartir el espacio.

## 8:00 – 10:00 · Conclusiones y limitaciones (Nolberto)

Abrir la pestaña **Conclusiones**.

- **Hallazgos:**
  - unas tres cuartas partes de los títulos son lecturas ágiles;
  - la calificación es igual en ambas áreas;
  - predominan el inglés y las editoriales académicas.
- **Hallazgo complementario (documento, sección 10.9):** las obras extensas son
  el 24 % de las obras, pero reúnen el 43,8 % de las calificaciones. Es un
  argumento para no reducir esa área solo por su número de títulos.
- **Recomendación:**
  - partir de un reparto cercano a 75 % / 25 % y ajustarlo hacia las obras
    extensas;
  - usar la pestaña de candidatos para revisar títulos;
  - contrastar con ventas, inventario y medidas reales de los estantes antes
    de decidir.
- **Limitaciones:**
  - no hay ventas, costos ni rentabilidad;
  - la ubicación en Nueva York es hipotética;
  - la población se limita a calificaciones de 3,5 o más;
  - el umbral de 350 páginas es una regla analítica;
  - no hay fechas para analizar tendencias.
- **Cierre:** el repositorio contiene el código, los datos preparados y el
  documento final en PDF (`AE4/documento/`).

## Lista de verificación antes de presentar

- [ ] La aplicación abre: la URL publicada o, si no, `streamlit run AE4/app.py`
      desde `ProyectoIntegrado` (probarlo en el computador de la clase).
- [ ] La primera carga del CSV tarda unos segundos: abrir la app antes de empezar.
- [ ] Los filtros están limpios para que las cifras coincidan con este guion.
- [ ] El PDF y el enlace del repositorio están adjuntos en la plataforma.
- [ ] Ensayaron una vez con cronómetro (10 minutos en total).
