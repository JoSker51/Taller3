# Taller 3 · Series de tiempo — Yomi Level

[![Abrir en Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/JoSker51/Taller3/blob/main/Taller3_Series_Tiempo_Yomi_Level.ipynb)

**Aprendizaje Supervisado · Universidad Sergio Arboleda**
José Santiago González · Oscar Mateo Arrubla · Leonardo Diasgranados · Docente: Hernán Cruz Bueno

**Sector:** aprendizaje de japonés con contenido audiovisual (anime, doramas y cine japonés).
**Variable objetivo:** dificultad promedio del japonés (1-100) de los títulos estrenados cada año, 1954-2025.

## Entregables

| Archivo | Contenido |
|---|---|
| [`Taller3_Series_Tiempo_Yomi_Level.docx`](Taller3_Series_Tiempo_Yomi_Level.docx) | Gráficas, respuestas A, B y C, preguntas 4 y 5, hoja de justificación de variables y hallazgos de cada modelo |
| [`Taller3_Series_Tiempo_Yomi_Level.ipynb`](Taller3_Series_Tiempo_Yomi_Level.ipynb) | Notebook ejecutado con todo el código y las gráficas |
| [`figuras/`](figuras/) | Las gráficas en PNG |

## Resumen

- El dataset (Moe-DB + AniList + TMDB, 9.977 títulos) solo trae el **año de estreno**, así que la serie es **anual** y usa datos reales, sin simular fechas.
- La dificultad promedio **baja de unos 33 puntos (años 50) a 21 (2025)**.
- **lag_1** (año anterior) es la variable más útil: desde 2012 se equivoca solo 0,36 puntos.
- Los rolling se calculan **solo con años anteriores** (`shift(1)`), para evitar fuga de datos.
- Con los 5 modelos de clase, **predecir el cambio** respecto al año anterior (en vez del nivel), usando `lag_2` y una ventana de 5 años, dio el mejor resultado: **SVM, R² 0,78**.

## Cómo ejecutar

**En Colab:** clic en el botón "Abrir en Colab" y luego *Entorno de ejecución → Ejecutar todas*. No hay que subir nada: el notebook descarga el dataset de este repositorio.

**En local:**

```bash
pip install pandas numpy scikit-learn matplotlib xgboost
jupyter notebook Taller3_Series_Tiempo_Yomi_Level.ipynb
```

El notebook lee `moe_db_anilist_dataset.csv`, que está en esta misma carpeta. `build_nb.py`, `textos.py` y `build_doc.py` regeneran el notebook y el documento Word.
