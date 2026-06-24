# ============================================================
#   MODELO DE APRENDIZAJE AUTOMÁTICO - BASE DE DATOS COVID-19
#   Fundamentos de Analítica de Datos
#   Ing. Marco Fernando Andrade Cedillo
# ============================================================

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

# ── PASO 1: CONECTAR CON LA BASE DE DATOS ────────────────────
print("Conectando con la base de datos Covid19_final...")

import os
DB_HOST = os.environ.get("DB_HOST", "localhost")
DB_PORT = os.environ.get("DB_PORT", "3306")
DB_USER = os.environ.get("DB_USER", "root")
DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

if DB_HOST == "localhost":
    engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final')
else:
    engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final?ssl_ca=&ssl_verify_cert=false')

# ── PASO 2: TRAER LOS DATOS CON SQL ──────────────────────────
query = """
SELECT
    nuevos,
    intervencion,
    cantidad,
    tarifa,
    dx,
    resclin,
    caso
FROM registro_a
"""

print("Cargando expedientes de pacientes...")
df = pd.read_sql(query, engine)

print(f"   Se cargaron {len(df):,} registros.")
print(f"   Columnas: {list(df.columns)}\n")

# ── PASO 3: LIMPIAR Y TRADUCIR LOS DATOS ─────────────────────
print("Traduciendo textos a numeros...")

columnas_texto = ['nuevos', 'intervencion', 'dx', 'resclin']

traductores = {}
for col in columnas_texto:
    le = LabelEncoder()
    df[col] = df[col].fillna('desconocido').astype(str)
    df[col] = le.fit_transform(df[col])
    traductores[col] = le
    print(f"   Columna '{col}' traducida.")

for col in ['cantidad', 'tarifa']:
    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

le_objetivo = LabelEncoder()
df['objetivo'] = le_objetivo.fit_transform(df['caso'].fillna('desconocido').astype(str))

print(f"\n   Estados posibles del paciente: {list(le_objetivo.classes_)}\n")

# ── PASO 4: SEPARAR PISTAS DEL RESULTADO FINAL ───────────────
X = df[['nuevos', 'intervencion', 'cantidad', 'tarifa', 'dx', 'resclin']]
y = df['objetivo']

# ── PASO 5: GUARDAR DATOS PARA EL EXAMEN FINAL ───────────────
X_train, X_test, y_train, y_test = train_test_split(
    X, y,
    test_size=0.2,
    random_state=42
)

print(f"Datos partidos:")
print(f"   Para estudiar  (entrenamiento): {len(X_train):,} registros")
print(f"   Para el examen (prueba):        {len(X_test):,} registros\n")

# ── PASO 6: REUNIR AL CONSEJO DE 100 SABIOS ──────────────────
print("Reuniendo al Consejo de los 100 Sabios del Bosque...")

sabios = RandomForestClassifier(
    n_estimators=100,
    random_state=42,
    n_jobs=-1
)

print("Los sabios estan leyendo todos los expedientes... (puede tardar 1-2 min)")
sabios.fit(X_train, y_train)
print("   Los sabios ya terminaron de estudiar!\n")

# ── PASO 7: REVISAR QUE VARIABLE PESA MAS ────────────────────
print("Importancia de cada variable (que datos pesan mas?):")
importancias = sabios.feature_importances_
for nombre, importancia in zip(X.columns, importancias):
    barra = "█" * int(importancia * 50)
    print(f"   {nombre:<15}: {importancia:.3f}  {barra}")

print()

# ── PASO 8: PONERLE EL EXAMEN A LOS SABIOS ───────────────────
print("Aplicando el examen sorpresa a los Sabios...")
predicciones = sabios.predict(X_test)

exactitud = accuracy_score(y_test, predicciones)
print(f"   Exactitud del Consejo: {exactitud:.2%}\n")

# Detectamos solo las clases que realmente aparecieron en el examen
clases_en_examen = np.unique(np.concatenate([y_test, predicciones]))
nombres_clases   = le_objetivo.inverse_transform(clases_en_examen)

print("BOLETA DE CALIFICACIONES DEL CONSEJO DE SABIOS:")
print("=" * 60)
print(classification_report(y_test, predicciones,
                             labels=clases_en_examen,
                             target_names=nombres_clases))

# ── PASO 9: PREDECIR UN PACIENTE NUEVO ───────────────────────
print("\nLLEGA UN PACIENTE NUEVO AL CONSULTORIO...")

paciente_nuevo = [[0, 0, 3, 1500, 0, 0]]
prediccion     = sabios.predict(paciente_nuevo)
estado_predicho = le_objetivo.inverse_transform(prediccion)[0]

print(f"   El Consejo dictamina que el paciente sera: {estado_predicho.upper()}")
print("\nPractica completada con exito!")