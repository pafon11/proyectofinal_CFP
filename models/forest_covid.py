# ============================================================
#   MODELO DE APRENDIZAJE AUTOMÁTICO - BASE DE DATOS COVID-19
#   Fundamentos de Analítica de Datos
#   Ing. Marco Fernando Andrade Cedillo
# ============================================================

import os
import pickle
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report, accuracy_score

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'forest_model.pkl')

def entrenar_y_guardar():
    print("Conectando con la base de datos Covid19_final...")

    DB_HOST = os.environ.get("DB_HOST", "localhost")
    DB_PORT = os.environ.get("DB_PORT", "3306")
    DB_USER = os.environ.get("DB_USER", "root")
    DB_PASSWORD = os.environ.get("DB_PASSWORD", "")

    if DB_HOST == "localhost":
        engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final')
    else:
        engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final?ssl_ca=&ssl_verify_cert=false')

    query = """
    SELECT nuevos, intervencion, cantidad, tarifa, dx, resclin, caso
    FROM registro_a
    """

    print("Cargando expedientes de pacientes...")
    df = pd.read_sql(query, engine)
    print(f"   Se cargaron {len(df):,} registros.")

    columnas_texto = ['nuevos', 'intervencion', 'dx', 'resclin']
    traductores = {}
    for col in columnas_texto:
        le = LabelEncoder()
        df[col] = df[col].fillna('desconocido').astype(str)
        df[col] = le.fit_transform(df[col])
        traductores[col] = le

    for col in ['cantidad', 'tarifa']:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    le_objetivo = LabelEncoder()
    df['objetivo'] = le_objetivo.fit_transform(df['caso'].fillna('desconocido').astype(str))

    X = df[['nuevos', 'intervencion', 'cantidad', 'tarifa', 'dx', 'resclin']]
    y = df['objetivo']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    print("Entrenando Random Forest...")
    sabios = RandomForestClassifier(n_estimators=50, random_state=42, n_jobs=-1)
    sabios.fit(X_train, y_train)
    print("   Entrenamiento completado!")

    predicciones = sabios.predict(X_test)
    exactitud = accuracy_score(y_test, predicciones)
    importancias = sabios.feature_importances_

    clases_en_examen = np.unique(np.concatenate([y_test, predicciones]))
    nombres_clases = le_objetivo.inverse_transform(clases_en_examen)

    from sklearn.metrics import classification_report
    reporte_dict = classification_report(
        y_test, predicciones,
        labels=clases_en_examen,
        target_names=nombres_clases,
        output_dict=True
    )

    paciente_nuevo = [[0, 0, 3, 1500, 0, 0]]
    prediccion = sabios.predict(paciente_nuevo)
    estado_predicho = le_objetivo.inverse_transform(prediccion)[0]

    bundle = {
        'sabios': sabios,
        'X': X,
        'importancias': importancias,
        'exactitud': exactitud,
        'y_test': y_test,
        'predicciones': predicciones,
        'le_objetivo': le_objetivo,
        'estado_predicho': estado_predicho,
        'traductores': traductores,
        'reporte_dict': reporte_dict,
        'nombres_clases': nombres_clases,
    }

    with open(MODEL_PATH, 'wb') as f:
        pickle.dump(bundle, f)
    print(f"   Modelo guardado en {MODEL_PATH}")
    return bundle

def cargar_modelo():
    if os.path.exists(MODEL_PATH):
        print("Cargando modelo pre-entrenado...")
        with open(MODEL_PATH, 'rb') as f:
            return pickle.load(f)
    else:
        return entrenar_y_guardar()

# Al importar el módulo, carga o entrena
_bundle = cargar_modelo()

sabios        = _bundle['sabios']
X             = _bundle['X']
importancias  = _bundle['importancias']
exactitud     = _bundle['exactitud']
y_test        = _bundle['y_test']
predicciones  = _bundle['predicciones']
le_objetivo   = _bundle['le_objetivo']
estado_predicho = _bundle['estado_predicho']