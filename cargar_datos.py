import os
import pandas as pd
import sqlite3

def cargar():
    salir = False
    while not salir:
        print("\n=============================")
        print("       Carga de Datos       ")
        print("=============================")
        print("Seleccione el tipo de archivo a cargar:")
        print("  [1] CSV")
        print("  [2] Excel")
        print("  [3] SQLite")
        print("  [4] Volver al menú principal")

        opcion = int(input("Seleccione una opción: "))

        if opcion == 1:
            csv()
        elif opcion == 2:
            excel()
        elif opcion == 3:
            sqlite()
        elif opcion == 4:
            salir = True  # Termina el bucle y vuelve al menú principal
        else:
            print("Opción inválida. Intente de nuevo.")

def csv():
    ruta = input("Ingrese la ruta del archivo CSV: ")
    if not os.path.isfile(ruta) or not ruta.endswith(".csv"): # Verifica si se cumplen los requisitos
        print("Error: Archivo no válido.")
        return # Termina la ejecución y los datos no se cargan MIRAR!!!!!!!!!!!!!!!!!

    data = pd.read_csv(ruta) # Carga el archivo y muestra los datos
    mostrar(data, ruta)

def excel(): # Lo mismo con excel
    ruta = input("Ingrese la ruta del archivo Excel: ")
    if not os.path.isfile(ruta) or not ruta.endswith(".xlsx"):
        print("Error: Archivo no válido.")
        return

    data = pd.read_excel(ruta)
    mostrar(data, ruta)

def sqlite():
    ruta = input("Ingrese la ruta de la base de datos SQLite: ")
    if not os.path.isfile(ruta) or not ruta.endswith(".db"):
        print("Error: Archivo no válido.")
        return

    conexion = sqlite3.connect(ruta) # Establece una conexión con la base de datos de SQlite
    cursor = conexion.cursor() # Cursor para ejecutar comandos de SQL

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';") # Obtiene los nombres de las tablas
    tablas = cursor.fetchall() # Recupera el resultado
    if not tablas:
        print("No hay tablas en la base de datos.")
        conexion.close() # Cierra la conexión
        return

    print("Tablas disponibles en la base de datos:")
    for i, (tabla,) in enumerate(tablas, 1): # Itera sobre las tablas y las enumera
        print(f"  [{i}] {tabla}") # Índice de tabla y nombre
 
    seleccion = input("Seleccione una tabla: ")
    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(tablas)): 
        print("Selección inválida.")
        conexion.close() # Si no es válido cierra la conexión
    else:
        tabla_seleccionada = tablas[int(seleccion) - 1][0] # Obtiene el nombre de la tabla
        data = pd.read_sql(f"SELECT * FROM {tabla_seleccionada}", conexion) # Obtiene todos los datos de la tabla
        conexion.close()
        mostrar(data, tabla_seleccionada)

def mostrar(data, fuente):
    print("\nDatos cargados correctamente.")
    print(f"Fuente: {fuente}")
    print(f"Número de filas: {data.shape[0]}")
    print(f"Número de columnas: {data.shape[1]}")
    print("\nPrimeras 5 filas:")
    print(data.head())
