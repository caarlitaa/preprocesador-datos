from menu import mostrar_menu, cerrar, cargar_datos, mostrar_datos, seleccion_terminal
import os
import pandas as pd
import sqlite3

class Datos:
    def __init__(self, file_path=None):
        self.ruta = None
        self.datos = None
        self.features = []
        self.targets = None
        self.paso = 1

        self.proceso()

    def proceso(self):
        while True:
            opcion = mostrar_menu(self.paso)
            if opcion == "1":  # Cargar datos
                if self.paso == 1 and not self.datos: # Verifica si los datos ya fueron cargados
                    self.opcion1_carga()
                else:
                    print(" Los datos ya están cargados.")
            
            elif opcion == "2" and self.paso == 2:
                self.paso = 2.1
            elif opcion == "2.1" and self.paso >= 2.1:
                self.opcion2_selector()


            elif opcion == "5":
                cerrar()

            else:
                print("Opción inválida.")

    def opcion1_carga(self):
        opcion, ruta = cargar_datos()
        if ruta is None:
            return
        
        if not os.path.exists(ruta):
            print("No existe la tabla")
            return
        
        extensiones = (
        (opcion == "1" and ruta.endswith('.csv')) or
        (opcion == "2" and (ruta.endswith('.xlsx') or ruta.endswith('.xls'))) or
        (opcion == "3" and (ruta.endswith('.sqlite') or ruta.endswith('.db')))
    )
        if not extensiones:
            print('Archivo inválido: el tipo no coincide con la opción seleccionada')
        else:
            try:
                if ruta.endswith('.csv'):
                    self.datos = pd.read_csv(ruta)
                    mostrar_datos(self.datos,ruta)
                    self.paso = 2
                elif ruta.endswith('.xlsx') or ruta.endswith('.xls'):
                    self.datos = pd.read_excel(ruta)
                    mostrar_datos(self.datos,ruta)
                    self.paso = 2
                elif ruta.endswith('.sqlite') or ruta.endswith('.db'):
                    conn = sqlite3.connect(ruta)
                    query = "SELECT name FROM sqlite_master WHERE type='table';"
                    tables = pd.read_sql(query, conn)
                    
                    if tables.empty:
                        raise ValueError("No se encontraron tablas disponibles.")
                    
                    print("Tablas disponibles en la base de datos:")
                    for i, table in enumerate(tables['name'], 1):
                        print(f"  [{i}] {table}")

                    seleccion = input("Seleccione una tabla: ")
                    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(tables)):
                        raise ValueError("Selección inválida.")

                    tabla_seleccionada = tables.iloc[int(seleccion) - 1]['name']
                    self.datos = pd.read_sql(f"SELECT * FROM {tabla_seleccionada}", conn)
                    conn.close()
                    
                    mostrar_datos(self.datos,ruta)
                    print(f"Los datos de {tabla_seleccionada} fueron cargados correctamente")
                    self.paso = 2
                else:
                    raise ValueError("Formato de archivo no compatible. Soportados: CSV, Excel y SQLite.")
            except Exception as e:
                raise ValueError(f"Error al importar datos: {str(e)}")

    def opcion2_selector(self):
        self.features, self.targets = seleccion_terminal(list(self.datos.columns))
        self.paso = 2.2
