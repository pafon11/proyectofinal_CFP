import mysql.connector
from mysql.connector import Error
import os

class RegresionVentas:
    def __init__(self):
        self.conexion  = None
        self.inversiones = []
        self.ventas      = []
        self.num_datos   = 0
        self.B0 = 0
        self.B1 = 0

    # ── Conexión ─────────────────────────────────────────────
    def conectar_mysql(self):
        try:
            self.conexion = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 3306)),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                database="ventas_db",
                ssl_disabled=not bool(os.environ.get("DB_HOST"))
            )
            print("✓ Conexión a MySQL establecida correctamente\n")
            return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return False

    # ── Leer datos ───────────────────────────────────────────
    def leer_datos_mysql(self):
        try:
            cursor = self.conexion.cursor()
            cursor.execute("SELECT inversion, ventas FROM registros_ventas ORDER BY id")
            resultados = cursor.fetchall()
            self.inversiones.clear()
            self.ventas.clear()

            self.num_datos = len(resultados)
            print(f" Registros encontrados en BD: {self.num_datos}\n")

            if self.num_datos == 0:
                print("⚠ No hay datos en la tabla\n")
                cursor.close()
                return False

            print(f"{'Inversión':<14} {'Ventas':<15}")
            print(f"{'-----------':<14} {'----------':<15}")

            for inv, ven in resultados:
                self.inversiones.append(float(inv))
                self.ventas.append(float(ven))
                print(f"${float(inv):<13.2f} ${float(ven):<14.2f}")

            print()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error al leer datos: {e}")
            return False

    # ── Guardar en BD ────────────────────────────────────────
    def guardar_en_bd(self, inversion, ventas, mes):
        try:
            cursor = self.conexion.cursor()
            cursor.execute(
                "INSERT INTO registros_ventas (mes, inversion, ventas) VALUES (%s, %s, %s)",
                (mes, inversion, ventas)
            )
            self.conexion.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error al guardar: {e}")
            return False

    # ── Validaciones ─────────────────────────────────────────
    def validar_inversion(self, inversion):
        if inversion < 0:
            print("❌ ERROR: La inversión no puede ser NEGATIVA\n")
            return False
        if inversion == 0:
            print("❌ ERROR: La inversión debe ser MAYOR a 0\n")
            return False
        return True

    def validar_mes(self, mes):
        if not mes:
            print("❌ ERROR: El mes no puede estar VACÍO\n")
            return False
        if not all(c.isalpha() or c == ' ' for c in mes):
            print("❌ ERROR: El mes debe contener SOLO LETRAS\n")
            return False
        return True

    # ── Calcular regresión ───────────────────────────────────
    def calcular_regresion(self):
        n = self.num_datos
        if n < 2:
            print("⚠ Se necesitan al menos 2 datos\n")
            return

        suma_x  = sum(self.inversiones)
        suma_y  = sum(self.ventas)
        suma_xy = sum(i * v for i, v in zip(self.inversiones, self.ventas))
        suma_x2 = sum(i * i for i in self.inversiones)

        xp = suma_x / n
        yp = suma_y / n

        num = sum((i - xp) * (v - yp) for i, v in zip(self.inversiones, self.ventas))
        den = sum((i - xp) ** 2 for i in self.inversiones)

        if den == 0:
            print("⚠ No se puede calcular: todos los datos de inversión son iguales\n")
            return

        self.B1 = num / den
        self.B0 = yp - self.B1 * xp

        print("═══════════════════════════════════════════")
        print("       CÁLCULOS DE REGRESIÓN LINEAL")
        print("═══════════════════════════════════════════\n")
        print(f"Número de datos (n): {n}")
        print(f"Σx = {suma_x:.2f}")
        print(f"Σy = {suma_y:.2f}")
        print(f"Σxy = {suma_xy:.2f}")
        print(f"Σx² = {suma_x2:.2f}\n")
        print(f"Promedio de X (x̄): {xp:.2f}")
        print(f"Promedio de Y (ȳ): {yp:.2f}\n")
        print(f"Numerador (Σ(xi - x̄)(yi - ȳ)): {num:.2f}")
        print(f"Denominador (Σ(xi - x̄)²): {den:.2f}\n")
        print("═══════════════════════════════════════════")
        print("          ECUACIÓN DE REGRESIÓN")
        print("═══════════════════════════════════════════\n")
        print(f"B₁ = {self.B1:.2f}")
        print(f"B₀ = {self.B0:.2f}\n")
        print(f"ŷ = {self.B0:.2f} + {self.B1:.2f} * x\n")

    # ── Hacer predicción ─────────────────────────────────────
    def hacer_prediccion(self, inversion):
        ventas_pred = self.B0 + self.B1 * inversion
        print("═══════════════════════════════════════════")
        print("              PREDICCIÓN")
        print("═══════════════════════════════════════════\n")
        print(f"Inversión: ${inversion:.2f}")
        print(f"Ventas predichas: ${ventas_pred:.2f}\n")
        print("═══════════════════════════════════════════\n")
        return ventas_pred

if __name__ == "__main__":
    prog = RegresionVentas()
    prog.conectar_mysql()
