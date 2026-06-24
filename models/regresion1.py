import mysql.connector
from mysql.connector import Error
import math
import os

class RegresionBackup:
    def __init__(self):
        self.conexion = None
        self.usuarios = []
        self.backup = []
        self.num_datos = 0
        self.B0 = 0
        self.B1 = 0
    
    # coneccion a la base de datos
    def conectar_mysql(self):
        try:
            self.conexion = mysql.connector.connect(
                host=os.environ.get("DB_HOST", "localhost"),
                port=int(os.environ.get("DB_PORT", 3306)),
                user=os.environ.get("DB_USER", "root"),
                password=os.environ.get("DB_PASSWORD", ""),
                database="almacen",
                ssl_disabled=not bool(os.environ.get("DB_HOST"))
            )
            print("✓ Conexión a MySQL establecida correctamente\n")
            return True
        except Error as err:
            if err.errno == 2003:
                print(f"❌ Error: No se puede conectar al servidor MySQL")
            else:
                print(f"❌ Error: {err}")
            return False
    
    # Lee los datos de la base
    def leer_datos_mysql(self):
        try:
            cursor = self.conexion.cursor()
            query = "SELECT usuarios, backup FROM backups ORDER BY id"
            cursor.execute(query)
            
            resultados = cursor.fetchall()
            self.num_datos = len(resultados)
            print(f"Registros encontrados en BD: {self.num_datos}\n")
            if self.num_datos == 0:
                print("⚠ No hay datos en la tabla\n")
                cursor.close()
                return False
            
            self.usuarios = []
            self.backup = []
            
            print(f"{'Usuarios (miles)':<20} {'Backup (GB)':<20}")
            print(f"{'-' * 15:<20} {'-' * 15:<20}")
            
            for (usuarios, backup) in resultados:
                self.usuarios.append(usuarios)
                self.backup.append(backup)
                print(f"{usuarios:<20.2f} {backup:<20.2f}")
            
            print()
            cursor.close()
            return True
            
        except Error as err:
            print(f"❌ Error al leer datos: {err}\n")
            return False
    
    # guardar en la base de datos la prediccion
    def guardar_en_bd(self, usuarios, backup):
        try:
            cursor = self.conexion.cursor()
            query = "INSERT INTO backups (usuarios, backup) VALUES (%s, %s)"
            valores = (usuarios, backup)
            cursor.execute(query, valores)
            self.conexion.commit()
            cursor.close()
            return True
        except Error as err:
            print(f"❌ Error al guardar: {err}")
            return False
    
    # Validacion para solo numeros positivos
    def validar_usuarios(self, usuarios):
        if usuarios < 0:
            print("❌ ERROR: La cantidad de usuarios no puede ser NEGATIVA")
            print("   Ingresa un valor positivo\n")
            return False
        if usuarios == 0:
            print("❌ ERROR: La cantidad de usuarios debe ser MAYOR a 0\n")
            return False
        return True
    
    # calcula la regresion
    def calcular_regresion(self):
        if self.num_datos < 2:
            print("⚠ Se necesitan al menos 2 datos para regresión lineal\n")
            return
        
        suma_x = sum(self.usuarios)
        suma_y = sum(self.backup)
        suma_xy = sum(u * b for u, b in zip(self.usuarios, self.backup))
        suma_x2 = sum(u * u for u in self.usuarios)
        
        x_promedio = suma_x / self.num_datos
        y_promedio = suma_y / self.num_datos
        
        numerador = sum((u - x_promedio) * (b - y_promedio) 
                       for u, b in zip(self.usuarios, self.backup))
        denominador = sum((u - x_promedio) ** 2 for u in self.usuarios)
        
        if denominador == 0:
            print("⚠ No se puede calcular: todos los datos son iguales\n")
            return
        
        self.B1 = numerador / denominador
        self.B0 = y_promedio - self.B1 * x_promedio
        
        print("═══════════════════════════════════════════")
        print("       CÁLCULOS DE REGRESIÓN LINEAL")
        print("═══════════════════════════════════════════\n")
        
        print(f"Número de datos (n): {self.num_datos}")
        print(f"Σx = {suma_x:.2f}")
        print(f"Σy = {suma_y:.2f}")
        print(f"Σxy = {suma_xy:.2f}")
        print(f"Σx² = {suma_x2:.2f}\n")
        
        print(f"Promedio de X (x̄): {x_promedio:.2f}")
        print(f"Promedio de Y (ȳ): {y_promedio:.2f}\n")
        
        print(f"Numerador (Σ(xi - x̄)(yi - ȳ)): {numerador:.2f}")
        print(f"Denominador (Σ(xi - x̄)²): {denominador:.2f}\n")
        
        print("═══════════════════════════════════════════")
        print("          ECUACIÓN DE REGRESIÓN")
        print("═══════════════════════════════════════════\n")
        print(f"B₁ = {self.B1:.2f}")
        print(f"B₀ = {self.B0:.2f}\n")
        print(f"ŷ = {self.B0:.2f} + {self.B1:.2f} * x\n")
    
    # HACER PREDICCIÓN
    def hacer_prediccion(self, usuarios):
        backup_predicho = self.B0 + self.B1 * usuarios
        
        print("═══════════════════════════════════════════")
        print("              PREDICCIÓN")
        print("═══════════════════════════════════════════\n")
        print(f"Usuarios: {usuarios:.2f} miles")
        print(f"Backup predicho: {backup_predicho:.2f} GB\n")
        print("═══════════════════════════════════════════\n")
        
        return backup_predicho
    
    # MOSTRAR MENÚ
    def mostrar_menu(self):
        print("\n╔════════════════════════════════════════════╗")
        print("║              MENÚ PRINCIPAL                ║")
        print("╠════════════════════════════════════════════╣")
        print("║ 1. Leer datos de BD y calcular regresión   ║")
        print("║ 2. Hacer predicción de tamaño de backup    ║")
        print("║ 3. Ver todos los datos actuales            ║")
        print("║ 4. Salir                                   ║")
        print("╚════════════════════════════════════════════╝\n")
        return input("Elige una opción (1-4): ").strip()
    
    # OPCIÓN 1: LEER DATOS Y CALCULAR
    def opcion_1(self):
        print("🔄 Leyendo datos de la base de datos...\n")
        if self.leer_datos_mysql():
            self.calcular_regresion()
            print("✓ Regresión calculada correctamente\n")
        else:
            print("✗ No se pudieron leer datos\n")
    
    # OPCIÓN 2: HACER PREDICCIÓN
    def opcion_2(self):
        if self.num_datos <= 0:
            print("⚠ PRIMERO debes usar OPCIÓN 1 para leer datos\n")
        else:
            usuarios_valido = False
            usuarios = 0
            
            while not usuarios_valido:
                try:
                    usuarios = float(input("Ingresa la cantidad de usuarios a predecir (miles): "))
                    if self.validar_usuarios(usuarios):
                        usuarios_valido = True
                except ValueError:
                    print("❌ ERROR: Debes ingresar un NÚMERO válido")
                    print("   No se aceptan letras ni caracteres especiales\n")
            
            print()
            backup_predicho = self.hacer_prediccion(usuarios)
            
            respuesta = input("¿Deseas guardar los datos de esta predicción en la BD? (s/n): ").strip().lower()
            print()
            
            if respuesta == 's':
                if self.guardar_en_bd(usuarios, backup_predicho):
                    print("\n✅ ÉXITO: El dato se guardó en la BD")
                    print(f"   Usuarios: {usuarios:.2f} miles")
                    print(f"   Backup: {backup_predicho:.2f} GB\n")
                else:
                    print("❌ ERROR: No se pudo guardar en BD\n")
            elif respuesta == 'n':
                print("ℹ️  El dato NO se guardó en la BD\n")
            else:
                print("⚠ Opción no válida\n")
    
    # OPCIÓN 3: VER DATOS
    def opcion_3(self):
        if self.num_datos <= 0:
            print("⚠ No hay datos cargados. Usa la opción 1 primero\n")
        else:
            print("═══════════════════════════════════════════")
            print("        DATOS ACTUALES EN MEMORIA")
            print("═══════════════════════════════════════════\n")
            print(f"{'Usuarios (miles)':<20} {'Backup (GB)':<20}")
            print(f"{'-' * 15:<20} {'-' * 15:<20}")
            
            for u, b in zip(self.usuarios, self.backup):
                print(f"{u:<20.2f} {b:<20.2f}")
            
            print()
            print(f"Total de registros: {self.num_datos}")
            print("═══════════════════════════════════════════\n")
    
    # EJECUTAR PROGRAMA
    def ejecutar(self):
        print("\n╔════════════════════════════════════════════╗")
        print("║  REGRESIÓN LINEAL - PREDICCIÓN DE BACKUP   ║")
        print("║  Lectura DINÁMICA desde MySQL              ║")
        print("║  CON VALIDACIONES                          ║")
        print("╚════════════════════════════════════════════╝\n")
        
        if not self.conectar_mysql():
            return
        
        salir = False
        
        while not salir:
            opcion = self.mostrar_menu()
            
            if opcion == '1':
                self.opcion_1()
            elif opcion == '2':
                self.opcion_2()
            elif opcion == '3':
                self.opcion_3()
            elif opcion == '4':
                print("Saliendo...")
                salir = True
            else:
                print("⚠ Opción no válida. Intenta de nuevo\n")
        
        if self.conexion and self.conexion.is_connected():
            self.conexion.close()
        
        print("✓ Conexión cerrada")
        print("¡Programa finalizado!\n")


# EJECUTAR PROGRAMA
if __name__ == "__main__":
    programa = RegresionBackup()
    programa.ejecutar()