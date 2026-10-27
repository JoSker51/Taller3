# Genera el notebook del Taller 3 (series de tiempo) para Yomi Level.
# Uso: python build_nb.py  ->  Taller3_Series_Tiempo_Yomi_Level.ipynb (sin ejecutar)
import nbformat as nbf
import textos as T

nb = nbf.v4.new_notebook()
C = []
md = lambda s: C.append(nbf.v4.new_markdown_cell(s.strip()))
code = lambda s: C.append(nbf.v4.new_code_cell(s.strip()))

md(T.INTRO)

code(r'''
# ----------------------------------------
# 📦 LIBRERÍAS
# ----------------------------------------
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from xgboost import XGBRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
import os
os.makedirs('figuras', exist_ok=True)
plt.rcParams['figure.dpi'] = 110
''')

md(T.SERIE)
code(r'''
# ----------------------------------------
# 📅 CONSTRUIR LA SERIE ANUAL (datos reales, sin simular)
# ----------------------------------------
# El CSV puede estar junto al notebook (Colab) o en la carpeta datos/ del repositorio
ruta = 'moe_db_anilist_dataset.csv' if os.path.exists('moe_db_anilist_dataset.csv') else '../datos/moe_db_anilist_dataset.csv'
df = pd.read_csv(ruta)
df = df.dropna(subset=['start_year'])
df['anio'] = df['start_year'].astype(int)

# Desde 1954: antes de ese año hay entre 1 y 8 títulos por año, demasiado pocos para un promedio confiable
serie = (df[df['anio'] >= 1954]
         .groupby('anio')
         .agg(dificultad=('Overall Difficulty (1-100)', 'mean'),
              titulos=('Overall Difficulty (1-100)', 'size'),
              pct_anime=('entry_type', lambda t: t.str.startswith('anime').mean() * 100)))
df_ts = serie[['dificultad']].copy()

# ----------------------------------------
# ➕ CREAR LAGS Y ROLLINGS
# shift(1) antes del rolling: el promedio usa solo los años ANTERIORES, como dice la definición de clase.
# Sin el shift, el rolling incluiría el mismo año que queremos predecir (fuga de datos).
# ----------------------------------------
df_ts['lag_1'] = df_ts['dificultad'].shift(1)
df_ts['rolling_mean_3'] = df_ts['dificultad'].shift(1).rolling(window=3).mean()
df_ts['rolling_std_3'] = df_ts['dificultad'].shift(1).rolling(window=3).std()

print(f"{len(df_ts)} años ({df_ts.index.min()}–{df_ts.index.max()}), "
      f"{int(serie['titulos'].sum())} títulos en total")
serie.join(df_ts.drop(columns='dificultad')).round(2)
''')

code(r'''
# 1. Serie original: dificultad promedio por año + cuántos títulos la componen
fig, ax = plt.subplots(figsize=(11, 4.2))
ax.plot(df_ts['dificultad'], marker='o', color='orange', label='Dificultad promedio del año')
ax.set_title('Dificultad promedio del japonés en los títulos estrenados cada año')
ax.set_xlabel('Año de estreno'); ax.set_ylabel('Dificultad (1-100)'); ax.grid(True)
ax2 = ax.twinx()
ax2.bar(serie.index, serie['titulos'], color='gray', alpha=0.25, label='Títulos ese año')
ax2.set_ylabel('Títulos estrenados')
ax.set_zorder(ax2.get_zorder() + 1); ax.patch.set_visible(False)
h1, l1 = ax.get_legend_handles_labels(); h2, l2 = ax2.get_legend_handles_labels()
ax.legend(h1 + h2, l1 + l2, loc='upper right')
plt.tight_layout(); plt.savefig('figuras/0_serie.png'); plt.show()
''')
md(T.OBS_SERIE)

md('## 1. Las tres gráficas pedidas')
code(r'''
# 2. Dificultad real + Lag 1
plt.figure(figsize=(11, 4))
plt.plot(df_ts['dificultad'], marker='o', label='Dificultad real', color='orange')
plt.plot(df_ts['lag_1'], marker='x', linestyle='--', label='Lag 1 (año anterior)', color='blue')
plt.title('Dificultad real y Lag 1')
plt.xlabel('Año de estreno'); plt.ylabel('Dificultad (1-100)')
plt.grid(True); plt.legend(); plt.tight_layout(); plt.savefig('figuras/1_lag1.png'); plt.show()

dif_lag = (df_ts['dificultad'] - df_ts['lag_1']).abs()
print(f"Correlación real vs lag_1: {df_ts['dificultad'].corr(df_ts['lag_1']):.2f}")
print(f"Diferencia promedio entre un año y el anterior: {dif_lag.mean():.2f} puntos")
print("Años donde lag_1 más se equivoca:")
print(dif_lag.sort_values(ascending=False).head(5).round(2).to_string())
''')

code(r'''
# 3. Dificultad real + promedio móvil de 3 años (y de 5 años para comparar la ventana)
rm5 = df_ts['dificultad'].shift(1).rolling(5).mean()
plt.figure(figsize=(11, 4))
plt.plot(df_ts['dificultad'], marker='o', label='Dificultad real', color='orange')
plt.plot(df_ts['rolling_mean_3'], marker='s', linestyle='-.', label='Rolling mean 3 años', color='green')
plt.plot(rm5, linestyle=':', linewidth=2, label='Rolling mean 5 años', color='darkgreen')
plt.title('Dificultad real y promedio móvil')
plt.xlabel('Año de estreno'); plt.ylabel('Dificultad (1-100)')
plt.grid(True); plt.legend(); plt.tight_layout(); plt.savefig('figuras/2_rolling_mean.png'); plt.show()
''')

code(r'''
# 4. Desviación estándar móvil (3 años)
plt.figure(figsize=(11, 4))
plt.plot(df_ts['rolling_std_3'], marker='d', linestyle='-', color='purple', label='Rolling std 3 años')
plt.title('Desviación estándar móvil (3 años)')
plt.xlabel('Año de estreno'); plt.ylabel('Desviación estándar (puntos)')
plt.grid(True); plt.legend(); plt.tight_layout(); plt.savefig('figuras/3_rolling_std.png'); plt.show()

print("Años con más variabilidad:"); print(df_ts['rolling_std_3'].nlargest(6).round(2).to_string())
print("\nPromedio de rolling_std_3 por época, junto a cuántos títulos se estrenaban por año:")
epoca = pd.cut(df_ts.index, [1953, 1979, 1999, 2011, 2025], labels=['1954-1979', '1980-1999', '2000-2011', '2012-2025'])
print(pd.DataFrame({'rolling_std_3': df_ts['rolling_std_3'], 'titulos_por_anio': serie['titulos']})
      .groupby(epoca, observed=True).mean().round(2).to_string())
''')

code(r'''
# 5. Gráfica combinada
plt.figure(figsize=(12, 6))
plt.plot(df_ts['dificultad'], marker='o', label='Dificultad real', color='orange')
plt.plot(df_ts['lag_1'], marker='x', linestyle='--', label='Lag 1 (año anterior)', color='blue')
plt.plot(df_ts['rolling_mean_3'], marker='s', linestyle='-.', label='Rolling mean 3 años', color='green')
plt.plot(df_ts['rolling_std_3'], marker='d', linestyle=':', label='Rolling std 3 años', color='purple')
plt.title('Dificultad con Lag, Media Móvil y Desviación Estándar')
plt.xlabel('Año de estreno'); plt.ylabel('Dificultad / Variabilidad')
plt.legend(); plt.grid(True); plt.tight_layout(); plt.savefig('figuras/4_combinada.png'); plt.show()
''')

md('## 2 y 3. Análisis y respuestas')
md(T.RESP_A)
md(T.RESP_B)
md(T.RESP_C)
md(T.RESP_5)
md(T.HOJA)

md(T.MODELOS_INTRO)
code(r'''
# ----------------------------------------
# 🎯 VARIABLES Y DIVISIÓN (sin mezclar el orden del tiempo)
# ----------------------------------------
datos = df_ts.dropna()
features = ['lag_1', 'rolling_mean_3', 'rolling_std_3']
X, y = datos[features], datos['dificultad']
corte = int(len(datos) * 0.8)
X_train, X_test, y_train, y_test = X.iloc[:corte], X.iloc[corte:], y.iloc[:corte], y.iloc[corte:]
print(f"Entrenamiento: {X_train.index.min()}–{X_train.index.max()} ({len(X_train)} años) | "
      f"Prueba: {X_test.index.min()}–{X_test.index.max()} ({len(X_test)} años)")
print(f"Rango de dificultad en entrenamiento: {y_train.min():.1f} a {y_train.max():.1f} | en prueba: {y_test.min():.1f} a {y_test.max():.1f}")

def modelos():
    return {
        "Regresión Lineal": LinearRegression(),
        "Random Forest": RandomForestRegressor(n_estimators=100, random_state=42),
        "XGBoost": XGBRegressor(objective='reg:squarederror', n_estimators=25, random_state=42, verbosity=0),
        "SVM": SVR(),
        "KNN": KNeighborsRegressor(n_neighbors=5)
    }

def entrenar(X_tr, y_tr, X_te):
    """Entrena los 5 modelos; SVM y KNN con datos escalados, como en clase."""
    sc = StandardScaler().fit(X_tr)
    pred = {}
    for nombre, modelo in modelos().items():
        if nombre in ["SVM", "KNN"]:
            pred[nombre] = modelo.fit(sc.transform(X_tr), y_tr).predict(sc.transform(X_te))
        else:
            pred[nombre] = modelo.fit(X_tr, y_tr).predict(X_te)
    return pred

def tabla(pred, real):
    return pd.DataFrame({k: {"MSE": mean_squared_error(real, v), "R2": r2_score(real, v),
                             "MAE (puntos)": mean_absolute_error(real, v)} for k, v in pred.items()}).T.round(2)

# Versión 1: como en clase, el modelo predice directamente el nivel de dificultad
pred_nivel = entrenar(X_train, y_train, X_test)
pred_nivel_tabla = dict(pred_nivel, **{"Ingenuo (= año anterior)": X_test['lag_1'].values})
tabla(pred_nivel_tabla, y_test)
''')

code(r'''
# 📈 GRÁFICA COMPARATIVA (versión 1: predecir el nivel)
plt.figure(figsize=(12, 5.5))
plt.plot(y_test.index, y_test.values, label='Real', linewidth=2.5, color='black', marker='o')
for nombre, p in pred_nivel.items():
    plt.plot(y_test.index, p, linestyle='--', label=nombre)
plt.axhline(y_train.min(), color='gray', linestyle=':', label='Mínimo visto en entrenamiento')
plt.title('Comparación de modelos: predecir directamente el nivel de dificultad')
plt.xlabel('Año de estreno'); plt.ylabel('Dificultad (1-100)')
plt.legend(); plt.grid(True); plt.tight_layout(); plt.savefig('figuras/5_comparativa_nivel.png'); plt.show()
''')
md(T.OBS_NIVEL)

code(r'''
# Versión 2: el modelo predice el CAMBIO respecto al año anterior (diferenciación)
# Las variables se expresan relativas al último valor conocido, así no dependen del nivel.
def relativas(d):
    r = pd.DataFrame(index=d.index)
    r['rm3_menos_lag1'] = d['rolling_mean_3'] - d['lag_1']
    r['rolling_std_3'] = d['rolling_std_3']
    return r

Xr = relativas(datos)
cambio = datos['dificultad'] - datos['lag_1']
pred_cambio = {k: X_test['lag_1'].values + v
               for k, v in entrenar(Xr.iloc[:corte], cambio.iloc[:corte], Xr.iloc[corte:]).items()}
pred_cambio_tabla = dict(pred_cambio, **{"Ingenuo (= año anterior)": X_test['lag_1'].values})
tabla(pred_cambio_tabla, y_test)
''')

code(r'''
# Versión 3: conjunto propuesto para el sector (lag_2 + ventana de 5 años), también prediciendo el cambio
p = df_ts['dificultad'].shift(1)
extra = pd.DataFrame({'lag_2': df_ts['dificultad'].shift(2),
                      'rolling_mean_5': p.rolling(5).mean(), 'rolling_std_5': p.rolling(5).std()})
datos5 = df_ts[['dificultad', 'lag_1']].join(extra).dropna()
X5 = pd.DataFrame({'lag2_menos_lag1': datos5['lag_2'] - datos5['lag_1'],
                   'rm5_menos_lag1': datos5['rolling_mean_5'] - datos5['lag_1'],
                   'rolling_std_5': datos5['rolling_std_5']})
c5 = int(len(datos5) * 0.8)
cambio5 = datos5['dificultad'] - datos5['lag_1']
base5, real5 = datos5['lag_1'].iloc[c5:].values, datos5['dificultad'].iloc[c5:]
pred_v3 = {k: base5 + v for k, v in entrenar(X5.iloc[:c5], cambio5.iloc[:c5], X5.iloc[c5:]).items()}
print(f"Prueba: {real5.index.min()}–{real5.index.max()} (los mismos años que las versiones 1 y 2)")
tabla(dict(pred_v3, **{"Ingenuo (= año anterior)": base5}), real5)
''')

code(r'''
# 📋 Resumen: R² de cada modelo en las tres versiones (mismos 14 años de prueba)
resumen = pd.DataFrame({
    'V1 nivel (lag_1, rm3, rs3)': tabla(pred_nivel_tabla, y_test)['R2'],
    'V2 cambio (lag_1, rm3, rs3)': tabla(pred_cambio_tabla, y_test)['R2'],
    'V3 cambio (lag_1, lag_2, rm5, rs5)': tabla(dict(pred_v3, **{"Ingenuo (= año anterior)": base5}), real5)['R2']})
resumen
''')

code(r'''
# ⚠️ Comprobación: ¿qué pasa si el rolling incluye el año que se predice (código de clase sin shift)?
fuga = pd.DataFrame({'lag_1': df_ts['lag_1'],
                     'rolling_mean_3': df_ts['dificultad'].rolling(3).mean(),
                     'rolling_std_3': df_ts['dificultad'].rolling(3).std(),
                     'dificultad': df_ts['dificultad']}).dropna()
cf = int(len(fuga) * 0.8)
pf = entrenar(fuga[features].iloc[:cf], fuga['dificultad'].iloc[:cf], fuga[features].iloc[cf:])
print("R² con fuga de datos (NO válido):")
print(tabla(pf, fuga['dificultad'].iloc[cf:])['R2'].to_string())
''')
md(T.OBS_FUGA)

md(T.POR_MODELO_INTRO)
code(r'''
# 📈 Una gráfica por modelo: real vs. predicción directa del nivel (V1) y predicción del cambio (V3)
colores = {"Regresión Lineal": 'royalblue', "Random Forest": 'forestgreen',
           "XGBoost": 'darkorange', "SVM": 'purple', "KNN": 'crimson'}
for i, (nombre, color) in enumerate(colores.items()):
    plt.figure(figsize=(10, 4))
    plt.plot(y_test.index, y_test.values, label='Real', linewidth=2.5, color='black', marker='o')
    plt.plot(y_test.index, pred_nivel[nombre], linestyle='--', color=color, alpha=0.55,
             label=f'{nombre}: predice el nivel (V1)')
    plt.plot(real5.index, pred_v3[nombre], linestyle='-', marker='s', color=color,
             label=f'{nombre}: predice el cambio (V3)')
    plt.title(f'Predicción anual usando {nombre}')
    plt.xlabel('Año de estreno'); plt.ylabel('Dificultad (1-100)')
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.savefig(f'figuras/6_{i}_{nombre.split()[0].lower()}.png'); plt.show()
''')
md(T.HALLAZGOS_MODELOS)
md(T.CONCLUSION)

nb['cells'] = C
nb['metadata'] = {'kernelspec': {'name': 'python3', 'display_name': 'Python 3', 'language': 'python'},
                  'language_info': {'name': 'python'}}
nbf.write(nb, 'Taller3_Series_Tiempo_Yomi_Level.ipynb')
print('notebook generado')
