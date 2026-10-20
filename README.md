# RepoMachine_ProInteg3
Repositorio para las actividades de Proyecto Integrado 3 de Analitica de Datos de Nolberto Gomez-AndresDavidMesa, Machine Learning- Nolberto Carmen Gomez Universidad IU Digital De Antioquia 

Este repositorio contiene la entrega de la Actividad 1 para la materia Proyecto Integrado III - Analitica de Datos. El proyecto se encarga de cargar el dataset publico pfaha/goodreads-books desde Hugging Face y procesarlo dentro del notebook actividad1.ipynb aplicando cuatro transformaciones basicas con Pandas como seleccion de columnas, renombrado al espanol, limpieza de nulos y filtrado por calificacion.

El flujo esta orquestado modularmente utilizando clases en Python guardadas en la carpeta src/ para la carga de datos y la generacion de reportes. Ademas, cuenta con un workflow en GitHub Actions que ejecuta automaticamente el notebook con cada push y guarda el resumen actualizado en un archivo de texto dentro de la carpeta reportes/.