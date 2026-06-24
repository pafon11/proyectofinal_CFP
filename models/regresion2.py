import mysql.connector
from mysql.connector import Error
import os

class RegresionEntrega:
    def __init__(self):
        self.conexion = None
        self.distancias = []
        self.tiempos = []
        self.num_datos = 0
        self.B0 = 0
        self.B1 = 0

    # Conexion a la base de datos
    def conectar_mysql(self):
        try:
            self.conexion = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 3306)),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                database="entregas_db",
                ssl_disabled=not bool(os.environ.get("DB_HOST"))
            )
            print("✓ Conexión a MySQL establecida correctamente\n")
            return True
        except Error as e:
            print(f"❌ Error de conexión: {e}")
            return False
        
    # Lee los datos de la base
    def leer_datos_mysql(self):
        try:
            cursor = self.conexion.cursor()
            query = "SELECT distancia, tiempo FROM entregas ORDER BY id"
            cursor.execute(query)
            resultados = cursor.fetchall()
            self.distancias.clear()
            self.tiempos.clear()
            for distancia, tiempo in resultados:
                self.distancias.append(distancia)
                self.tiempos.append(tiempo)
            self.num_datos = len(self.distancias)
            print(f"Registros encontrados en BD: {self.num_datos}\n")
            if self.num_datos == 0:
                print("⚠ No hay datos en la tabla\n")
                return False

            print(f"{'Distancia (km)':<20} {'Tiempo (min)':<20}")
            print(f"{'-' * 15:<20} {'-' * 15:<20}")
            for i in range(self.num_datos):
                print(
                    f"{self.distancias[i]:<20.2f} "
                    f"{self.tiempos[i]:<20.2f}"
                )
            print()
            cursor.close()
            return True

        except Error as e:
            print(f"❌ Error al leer datos: {e}")
            return False

    # para guardar en la base de datos "adición" al codigo original
    def guardar_en_bd(self, distancia, tiempo):
        try:
            cursor = self.conexion.cursor()
            query = """
            INSERT INTO entregas (distancia, tiempo)
            VALUES (%s, %s)
            """
            valores = (distancia, tiempo)
            cursor.execute(query, valores)
            self.conexion.commit()
            cursor.close()
            return True
        except Error as e:
            print(f"❌ Error al guardar: {e}")
            return False

    # Valida la distancia
    def validar_distancia(self, distancia):
        if distancia < 0:
            print("❌ ERROR: La distancia no puede ser NEGATIVA")
            print("Ingresa un valor positivo\n")
            return False
        if distancia == 0:
            print("❌ ERROR: La distancia debe ser MAYOR a 0\n")
            return False
        return True

    # calculo de la regresion
    def calcular_regresion(self):
        if self.num_datos < 2:
            print("⚠ Se necesitan al menos 2 datos\n")
            return

        suma_x = 0
        suma_y = 0
        suma_xy = 0
        suma_x2 = 0
        for i in range(self.num_datos):
            suma_x += self.distancias[i]
            suma_y += self.tiempos[i]
            suma_xy += (
                self.distancias[i]
                * self.tiempos[i]
            )

            suma_x2 += (
                self.distancias[i]
                * self.distancias[i]
            )

        x_promedio = suma_x / self.num_datos
        y_promedio = suma_y / self.num_datos
        numerador = 0
        denominador = 0

        for i in range(self.num_datos):
            numerador += (
                (self.distancias[i] - x_promedio)
                *
                (self.tiempos[i] - y_promedio)
            )
            denominador += (
                (self.distancias[i] - x_promedio) ** 2
            )
        if denominador == 0:
            print("⚠ No se puede calcular\n")
            return
        self.B1 = numerador / denominador
        self.B0 = y_promedio - (self.B1 * x_promedio)

        print("═══════════════════════════════════════════")
        print("       CÁLCULOS DE REGRESIÓN LINEAL")
        print("═══════════════════════════════════════════\n")
        print(f"Número de datos (n): {self.num_datos}")
        print(f"Σx = {suma_x:.2f}")
        print(f"Σy = {suma_y:.2f}")
        print(f"Σxy = {suma_xy:.2f}")
        print(f"Σx² = {suma_x2:.2f}\n")
        print(f"Promedio X = {x_promedio:.2f}")
        print(f"Promedio Y = {y_promedio:.2f}\n")
        print(f"Numerador = {numerador:.2f}")
        print(f"Denominador = {denominador:.2f}\n")
        print("═══════════════════════════════════════════")
        print("          ECUACIÓN DE REGRESIÓN")
        print("═══════════════════════════════════════════\n")

        print(f"B1 = {self.B1:.2f}")
        print(f"B0 = {self.B0:.2f}\n")
        print(f"ŷ = {self.B0:.2f} + {self.B1:.2f} * x\n")

    # Prediccion
    def hacer_prediccion(self, distancia):
        tiempo_predicho = (
            self.B0 + (self.B1 * distancia)
        )
        print("═══════════════════════════════════════════")
        print("              PREDICCIÓN")
        print("═══════════════════════════════════════════\n")
        print(f"Distancia: {distancia:.2f} km")
        print(
            f"Tiempo predicho: "
            f"{tiempo_predicho:.2f} minutos\n"
        )
        return tiempo_predicho

    def mostrar_menu(self):
        print(
            "\n╔════════════════════════════════════════════╗")
        print("║              MENÚ PRINCIPAL                ║")
        print("╠════════════════════════════════════════════╣")
        print("║ 1. Leer datos y calcular regresión         ║")
        print("║ 2. Hacer predicción                        ║")
        print("║ 3. Ver datos actuales                      ║")
        print("║ 4. Salir.                                  ║")
        print("╚════════════════════════════════════════════╝")
        return input("\nElige una opción: ")
    
    def opcion_1(self):
        print("\n🔄 Leyendo datos...\n")
        if self.leer_datos_mysql():
            self.calcular_regresion()
            print("✓ Regresión calculada correctamente\n")
        else:
            print("✗ No se pudieron leer datos\n")

    def opcion_2(self):
        if self.num_datos <= 0:
            print("⚠ Primero usa la opción 1\n")
            return
        valido = False
        distancia = 0
        while not valido:
            try:
                distancia = float(
                    input("Ingresa distancia: ")
                )
                if self.validar_distancia(distancia):
                    valido = True
            except ValueError:
                print("❌ Debes ingresar un número válido\n")
        print()
        tiempo_predicho = self.hacer_prediccion(distancia)
        respuesta = input(
            "¿Guardar en BD? (s/n): "
        ).lower()
        print()
        if respuesta == "s":
            if self.guardar_en_bd(
                distancia,
                tiempo_predicho
            ):
                print("✅ ÉXITO: Datos guardados")
            else:
                print("❌ Error al guardar\n")
        else:
            print("ℹ️ Datos no guardados\n")

    def opcion_3(self):
        if self.num_datos <= 0:
            print("⚠ No hay datos cargados\n")
            return
        print("═══════════════════════════════════════════")
        print("           DATOS EN MEMORIA")
        print("═══════════════════════════════════════════\n")
        print(f"{'Distancia (km)':<20} {'Tiempo (min)':<20}")
        print(f"{'-' * 15:<20} {'-' * 15:<20}")
        for i in range(self.num_datos):

            print(
                f"{self.distancias[i]:<20.2f} "
                f"{self.tiempos[i]:<20.2f}"
            )
        print()
        print(f"Total registros: {self.num_datos}")

    def ejecutar(self):
        print("\n╔════════════════════════════════════════════╗")
        print("║ REGRESIÓN LINEAL - PREDICCIÓN DE ENTREGA   ║")
        print("╚════════════════════════════════════════════╝\n")

        if not self.conectar_mysql():
            return
        salir = False
        while not salir:
            opcion = self.mostrar_menu()
            if opcion == "1":
                self.opcion_1()
            elif opcion == "2":
                self.opcion_2()
            elif opcion == "3":
                self.opcion_3()
            elif opcion == "4":
                salir = True
                print("Saliendo...")
            else:
                print("⚠ Opción inválida\n")
        if self.conexion.is_connected():
            self.conexion.close()
        print("✓ Programa finalizado")

if __name__ == "__main__":
    programa = RegresionEntrega()
    programa.ejecutar()