"""
ML Dashboard - Flask Application
Retorna datos estructurados JSON para renderizado visual en frontend.
"""
import sys, io, os, importlib.util
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

class CaptureOutput:
    def __enter__(self):
        self._buf = io.StringIO()
        self._old = sys.stdout
        sys.stdout = self._buf
        return self._buf
    def __exit__(self, *args):
        sys.stdout = self._old


# ── FOREST COVID-19 ──────────────────────────────────────────
def run_forest_covid():
    try:
        from models.forest_covid import (sabios, X, importancias, exactitud,
                                          y_test, predicciones, le_objetivo, estado_predicho)

        import numpy as np
        from sklearn.metrics import classification_report

        clases_en_examen = np.unique(np.concatenate([y_test, predicciones]))
        nombres_clases   = le_objetivo.inverse_transform(clases_en_examen)

        # Reporte como dict
        from sklearn.metrics import classification_report
        reporte_dict = classification_report(
            y_test, predicciones,
            labels=clases_en_examen,
            target_names=nombres_clases,
            output_dict=True
        )

        # Importancias como lista ordenada
        imp_list = sorted(
            [{"variable": n, "importancia": round(float(v), 4)}
             for n, v in zip(X.columns, importancias)],
            key=lambda x: x["importancia"], reverse=True
        )

        # Tabla del reporte (solo clases reales, sin avg rows)
        reporte_tabla = []
        for clase in nombres_clases:
            if clase in reporte_dict:
                r = reporte_dict[clase]
                reporte_tabla.append({
                    "clase": clase,
                    "precision": round(r["precision"], 3),
                    "recall":    round(r["recall"], 3),
                    "f1":        round(r["f1-score"], 3),
                    "support":   int(r["support"])
                })

        return {
            "status": "success",
            "exactitud": round(float(exactitud), 4),
            "exactitud_pct": f"{exactitud:.2%}",
            "estado_predicho": estado_predicho.upper(),
            "importancias": imp_list,
            "reporte": reporte_tabla,
            "n_train": int(len(X) * 0.8),
            "n_test":  int(len(X) * 0.2),
            "n_total": int(len(X)),
            "clases":  list(le_objetivo.classes_)
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


# ── REGRESIÓN 1 - BACKUP ─────────────────────────────────────
def run_regresion1(action, usuarios=None, guardar=False):
    from models.regresion1 import RegresionBackup
    resultado = {"status": "error", "error": ""}
    try:
        prog = RegresionBackup()
        with CaptureOutput():
            ok = prog.conectar_mysql()
        if not ok:
            resultado["error"] = "No se pudo conectar a MySQL. Verifica credenciales."
            return resultado

        with CaptureOutput():
            datos_ok = prog.leer_datos_mysql()

        if not datos_ok:
            resultado["error"] = "No hay datos en la tabla o no se pudieron leer."
            return resultado

        with CaptureOutput():
            prog.calcular_regresion()

        # Datos de la tabla
        datos = [{"x": u, "y": b} for u, b in zip(prog.usuarios, prog.backup)]

        # Estadísticas
        n    = prog.num_datos
        sx   = sum(prog.usuarios)
        sy   = sum(prog.backup)
        xp   = sx / n
        yp   = sy / n
        sxy  = sum(u*b for u,b in zip(prog.usuarios, prog.backup))
        sx2  = sum(u*u for u in prog.usuarios)
        num  = sum((u-xp)*(b-yp) for u,b in zip(prog.usuarios, prog.backup))
        den  = sum((u-xp)**2 for u in prog.usuarios)

        resultado.update({
            "status":   "success",
            "accion":   action,
            "datos":    datos,
            "n":        n,
            "suma_x":   round(sx, 2),
            "suma_y":   round(sy, 2),
            "suma_xy":  round(sxy, 2),
            "suma_x2":  round(sx2, 2),
            "xprom":    round(xp, 2),
            "yprom":    round(yp, 2),
            "numerador":   round(num, 2),
            "denominador": round(den, 2),
            "B0": round(prog.B0, 4),
            "B1": round(prog.B1, 4),
            "ecuacion": f"ŷ = {prog.B0:.2f} + {prog.B1:.2f} × x",
        })

        if action == "predecir" and usuarios is not None:
            with CaptureOutput():
                backup_pred = prog.hacer_prediccion(float(usuarios))
            resultado["prediccion"] = {
                "input_label": "Usuarios",
                "input_val":   float(usuarios),
                "input_unit":  "miles",
                "output_label":"Backup estimado",
                "output_val":  round(backup_pred, 2),
                "output_unit": "GB"
            }
            if guardar:
                with CaptureOutput():
                    saved = prog.guardar_en_bd(float(usuarios), backup_pred)
                resultado["guardado"] = saved

        with CaptureOutput():
            if prog.conexion and prog.conexion.is_connected():
                prog.conexion.close()
    except Exception as e:
        resultado["error"] = str(e)
    return resultado


# ── REGRESIÓN 2 - ENTREGA ─────────────────────────────────────
def run_regresion2(action, distancia=None, guardar=False):
    from models.regresion2 import RegresionEntrega
    resultado = {"status": "error", "error": ""}
    try:
        prog = RegresionEntrega()
        with CaptureOutput():
            ok = prog.conectar_mysql()
        if not ok:
            resultado["error"] = "No se pudo conectar a MySQL. Verifica credenciales."
            return resultado

        with CaptureOutput():
            datos_ok = prog.leer_datos_mysql()

        if not datos_ok:
            resultado["error"] = "No hay datos en la tabla o no se pudieron leer."
            return resultado

        with CaptureOutput():
            prog.calcular_regresion()

        datos = [{"x": d, "y": t} for d, t in zip(prog.distancias, prog.tiempos)]
        n   = prog.num_datos
        sx  = sum(prog.distancias)
        sy  = sum(prog.tiempos)
        xp  = sx / n
        yp  = sy / n
        sxy = sum(d*t for d,t in zip(prog.distancias, prog.tiempos))
        sx2 = sum(d*d for d in prog.distancias)
        num = sum((d-xp)*(t-yp) for d,t in zip(prog.distancias, prog.tiempos))
        den = sum((d-xp)**2 for d in prog.distancias)

        resultado.update({
            "status":   "success",
            "accion":   action,
            "datos":    datos,
            "n":        n,
            "suma_x":   round(sx, 2),
            "suma_y":   round(sy, 2),
            "suma_xy":  round(sxy, 2),
            "suma_x2":  round(sx2, 2),
            "xprom":    round(xp, 2),
            "yprom":    round(yp, 2),
            "numerador":   round(num, 2),
            "denominador": round(den, 2),
            "B0": round(prog.B0, 4),
            "B1": round(prog.B1, 4),
            "ecuacion": f"ŷ = {prog.B0:.2f} + {prog.B1:.2f} × x",
        })

        if action == "predecir" and distancia is not None:
            with CaptureOutput():
                tiempo_pred = prog.hacer_prediccion(float(distancia))
            resultado["prediccion"] = {
                "input_label":  "Distancia",
                "input_val":    float(distancia),
                "input_unit":   "km",
                "output_label": "Tiempo estimado",
                "output_val":   round(tiempo_pred, 2),
                "output_unit":  "min"
            }
            if guardar:
                with CaptureOutput():
                    saved = prog.guardar_en_bd(float(distancia), tiempo_pred)
                resultado["guardado"] = saved

        with CaptureOutput():
            if prog.conexion and prog.conexion.is_connected():
                prog.conexion.close()
    except Exception as e:
        resultado["error"] = str(e)
    return resultado


# ── RUTAS ────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/forest")
def forest():
    return render_template("forest.html")

@app.route("/forest/run", methods=["POST"])
def forest_run():
    return jsonify(run_forest_covid())

@app.route("/forest/opciones")
def forest_opciones():
    """Retorna los valores únicos de dx e intervencion desde la BD."""
    try:
        from sqlalchemy import create_engine, text
        DB_HOST = os.environ.get("DB_HOST", "localhost")
        DB_PORT = os.environ.get("DB_PORT", "3306")
        DB_USER = os.environ.get("DB_USER", "root")
        DB_PASSWORD = os.environ.get("DB_PASSWORD", "")
        if DB_HOST == "localhost":
            engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final')
        else:
            engine = create_engine(f'mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/Covid19_final?ssl_ca=&ssl_verify_cert=false')
        with engine.connect() as conn:
            dx_rows  = conn.execute(text("SELECT DISTINCT dx FROM registro_a WHERE dx IS NOT NULL ORDER BY dx LIMIT 80")).fetchall()
            int_rows = conn.execute(text("SELECT DISTINCT intervencion FROM registro_a WHERE intervencion IS NOT NULL ORDER BY intervencion LIMIT 80")).fetchall()
        return jsonify({
            "status": "success",
            "dx":          [r[0] for r in dx_rows  if r[0]],
            "intervencion": [r[0] for r in int_rows if r[0]]
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route("/forest/predecir", methods=["POST"])
def forest_predecir():
    """Predice el estado de un paciente nuevo con datos del formulario."""
    try:
        data = request.get_json() or {}

        from models.forest_covid import sabios, traductores, le_objetivo

        import pandas as pd

        # Construir fila con los valores del formulario
        fila = pd.DataFrame([{
            "nuevos":      data.get("nuevos", "desconocido"),
            "intervencion":data.get("intervencion", "desconocido"),
            "cantidad":    float(data.get("cantidad", 1)),
            "tarifa":      float(data.get("tarifa", 0)),
            "dx":          data.get("dx", "desconocido"),
            "resclin":     data.get("resclin", "desconocido"),
        }])

        # Aplicar los mismos LabelEncoders del entrenamiento
        for col in ["nuevos", "intervencion", "dx", "resclin"]:
            le = traductores[col]
            val = fila[col].iloc[0]
            # Si el valor no estaba en el entrenamiento, usar 0
            if val in le.classes_:
                fila[col] = le.transform([val])
            else:
                fila[col] = 0

        X_nuevo = fila[["nuevos","intervencion","cantidad","tarifa","dx","resclin"]]
        pred    = sabios.predict(X_nuevo)
        prob    = sabios.predict_proba(X_nuevo)[0]
        estado  = le_objetivo.inverse_transform(pred)[0]

        clases_labels = le_objetivo.classes_
        probabilidades = [{"clase": c, "prob": round(float(p)*100, 1)} for c, p in zip(clases_labels, prob)]
        probabilidades.sort(key=lambda x: x["prob"], reverse=True)

        return jsonify({
            "status":         "success",
            "estado_predicho": estado.upper(),
            "probabilidades":  probabilidades
        })
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)})

@app.route("/regresion1")
def regresion1():
    return render_template("regresion1.html")

@app.route("/regresion1/run", methods=["POST"])
def regresion1_run():
    d = request.get_json() or {}
    return jsonify(run_regresion1(
        action=d.get("action","calcular"),
        usuarios=d.get("usuarios"),
        guardar=d.get("guardar", False)
    ))

@app.route("/regresion2")
def regresion2():
    return render_template("regresion2.html")

@app.route("/regresion2/run", methods=["POST"])
def regresion2_run():
    d = request.get_json() or {}
    return jsonify(run_regresion2(
        action=d.get("action","calcular"),
        distancia=d.get("distancia"),
        guardar=d.get("guardar", False)
    ))

# ── REGRESIÓN 3 - VENTAS ─────────────────────────────────────
def run_regresion3(action, inversion=None, mes=None, guardar=False):
    from models.regresion3 import RegresionVentas
    resultado = {"status": "error", "error": ""}
    try:
        prog = RegresionVentas()
        with CaptureOutput():
            ok = prog.conectar_mysql()
        if not ok:
            resultado["error"] = "No se pudo conectar a MySQL. Verifica credenciales."
            return resultado

        with CaptureOutput():
            datos_ok = prog.leer_datos_mysql()
        if not datos_ok:
            resultado["error"] = "No hay datos en la tabla o no se pudieron leer."
            return resultado

        with CaptureOutput():
            prog.calcular_regresion()

        datos = [{"x": i, "y": v} for i, v in zip(prog.inversiones, prog.ventas)]
        n    = prog.num_datos
        sx   = sum(prog.inversiones)
        sy   = sum(prog.ventas)
        xp   = sx / n
        yp   = sy / n
        sxy  = sum(i*v for i,v in zip(prog.inversiones, prog.ventas))
        sx2  = sum(i*i for i in prog.inversiones)
        num  = sum((i-xp)*(v-yp) for i,v in zip(prog.inversiones, prog.ventas))
        den  = sum((i-xp)**2 for i in prog.inversiones)

        resultado.update({
            "status":      "success",
            "accion":      action,
            "datos":       datos,
            "n":           n,
            "suma_x":      round(sx, 2),
            "suma_y":      round(sy, 2),
            "suma_xy":     round(sxy, 2),
            "suma_x2":     round(sx2, 2),
            "xprom":       round(xp, 2),
            "yprom":       round(yp, 2),
            "numerador":   round(num, 2),
            "denominador": round(den, 2),
            "B0":          round(prog.B0, 4),
            "B1":          round(prog.B1, 4),
            "ecuacion":    f"ŷ = {prog.B0:.2f} + {prog.B1:.2f} × x",
        })

        if action == "predecir" and inversion is not None:
            with CaptureOutput():
                ventas_pred = prog.hacer_prediccion(float(inversion))
            resultado["prediccion"] = {
                "input_label":  "Inversión",
                "input_val":    float(inversion),
                "input_unit":   "MXN",
                "output_label": "Ventas estimadas",
                "output_val":   round(ventas_pred, 2),
                "output_unit":  "MXN"
            }
            if guardar and mes:
                with CaptureOutput():
                    saved = prog.guardar_en_bd(float(inversion), ventas_pred, mes)
                resultado["guardado"] = saved

        with CaptureOutput():
            if prog.conexion and prog.conexion.is_connected():
                prog.conexion.close()
    except Exception as e:
        resultado["error"] = str(e)
    return resultado


@app.route("/regresion3")
def regresion3():
    return render_template("regresion3.html")

@app.route("/regresion3/run", methods=["POST"])
def regresion3_run():
    d = request.get_json() or {}
    return jsonify(run_regresion3(
        action=d.get("action", "calcular"),
        inversion=d.get("inversion"),
        mes=d.get("mes"),
        guardar=d.get("guardar", False)
    ))


if __name__ == "__main__":
    app.run(debug=True, port=5000)