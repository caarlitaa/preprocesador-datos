from menu import mostrar_menu, cerrar, cargar_datos, mostrar_datos, seleccion_terminal
import os
import pandas as pd
import sqlite3
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, MinMaxScaler, StandardScaler


# Clase que maneja la carga y el preprocesamiento
class Datos: 
    def __init__(self, file_path=None):
        self.ruta = None
        self.datos = None
        self.features = []
        self.targets = None
        self.paso = 1
        self.preprocesado = False
    
        

        self.proceso() # Inicia el flujo del menú


    def proceso(self): 
        while True:
            opcion = mostrar_menu(self.paso, self.datos, self.ruta)

            if opcion == "1":  # Cargar datos
                if self.paso == 1 and not self.datos: # Verifica si los datos ya fueron cargados
                    self.opcion1_carga()
                else:
                    print(" Los datos ya están cargados.")
            
            elif opcion == "2" and self.paso == 2: # Preprocesamiento
                self.paso = 2.1 
            
            elif opcion == "2.1" and self.paso >= 2.1: # Selección de columnas 
                if not self.preprocesado:
                    self.opcion2_selector_columnas()
                else: 
                    print("No se pueden cambiar las columnas una vez que se inicia el preprocesado")
            elif opcion == "2.2" and self.paso >= 2.2: # Manejar valores faltantes
                self.preprocesado = True
                self.opcion2_manejo_nulos()
            elif opcion == "2.3" and self.paso >= 2.3: # Transformar datos categóricos
                self.opcion2_transformar_categoricos()
            elif opcion == "2.4" and self.paso >= 2.4: # Normalizar y escalar valores numéricas
                self.opcion2_normalizar_numericas()
            elif opcion == "2.5" and self.paso >= 2.5: # Manejar valores atípicos
                self.opcion2_manejo_atipicos()
                self.preprocesado = False
            
            elif opcion == "3" and self.paso >= 3: # Visualizar datos antes y después
                self.opcion3_visualizar_datos()
                self.preprocesado_comp = True
            
            elif opcion == "4" and self.paso >= 4: # Exportar los datos
                self.opcion4_exportar_datos()
            
            elif opcion == "5": # Paso para cerrar la app
                cerrar()
            
            else:
                print("Opción inválida.")

    
    def opcion1_carga(self): # Carga los datos según el  formato
        carga = cargar_datos()
        if carga is None:
            return
        opcion, ruta = carga
        if not ruta or not os.path.exists(ruta):
            print("Archivo no válido, inténtelo de nuevo")
            return
        
        # Verifica que la extensión coincida con la opción seleccionada
        extensiones = {1:'.csv', 2: ('.xlsx','.xls'), 3: ('.sqlite', '.db')}
        
        if not ruta.endswith(extensiones.get(opcion, '')):
            print('Archivo inválido: el tipo no coincide con la opción seleccionada')
            return
        try:
            if ruta.endswith('.csv'): # Carga de un archivo CSV
                    self.datos = pd.read_csv(ruta)
                
            elif ruta.endswith('.xlsx') or ruta.endswith('.xls'): # Carga de un archivo excel
                    self.datos = pd.read_excel(ruta)
                
            elif ruta.endswith('.sqlite') or ruta.endswith('.db'): # Carga dese una base de datos SQLite
                    conn = sqlite3.connect(ruta)
                    query = "SELECT name FROM sqlite_master WHERE type='table';"
                    tables = pd.read_sql(query, conn) # Obtiene las tablas de la base
                    
                    if tables.empty:
                        raise ValueError("No se encontraron tablas disponibles.")
                    
                    # Muestra las tablas disponibles y solicita la selección de una
                    print("Tablas disponibles en la base de datos:")
                    for i, table in enumerate(tables['name'], 1):
                        print(f"  [{i}] {table}")

                    seleccion = input("Seleccione una tabla: ") 
                    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(tables)):
                        raise ValueError("Selección inválida.")
                    
                    # Obtiene el nombre y carga sus datos
                    tabla_seleccionada = tables.iloc[int(seleccion) - 1]['name']
                    self.datos = pd.read_sql(f"SELECT * FROM {tabla_seleccionada}", conn)
                    conn.close()
                    
                    mostrar_datos(self.datos,ruta)
                    print(f"Los datos de {tabla_seleccionada} fueron cargados correctamente")
            
            mostrar_datos(self.datos, ruta)
            self.paso = 2
            self.ruta = ruta
                
                
        except Exception as e:
            raise ValueError(f"Error al importar datos: {str(e)}")

    # Selecciona las columnas de entrada y salida
    def opcion2_selector_columnas(self):
        self.features, self.targets = seleccion_terminal(list(self.datos.columns))
        self.paso = 2.2
    
    # Manejo de valores faltantes
    def opcion2_manejo_nulos(self):
        # Toma las columnas seleccionadas anteriormente y calcula cuantos valores faltantes
        seleccionadas = self.features + [self.targets] 
        valores_faltantes = self.datos[seleccionadas].isnull().sum()
        nulos = valores_faltantes[valores_faltantes > 0]
        
        # Si no hay nulos, informa de ello
        if nulos.empty:
            print("\n=============================")
            print("Manejo de Valores Faltantes")
            print("=============================")
            print("No se han detectado valores faltantes en las columnas seleccionadas.")
            print("No es necesario aplicar ninguna estrategia")
            self.paso = 2.3
            return
        
        # Si hay nulos los muestra
        print("\n=============================")
        print("Manejo de Valores Faltantes")
        print("=============================")
        print("Se han detectado valores faltantes en las siguientes columnas seleccionadas:")
        for columna, cantidad in nulos.items():
            print(f"  - {columna}: {cantidad} valores faltantes")
        
        # Opciones para manejarlos
        print("\nSeleccione una estrategia para manejar los valores faltantes:")
        print("  [1] Eliminar filas con valores faltantes")
        print("  [2] Rellenar con la media de la columna")
        print("  [3] Rellenar con la mediana de la columna")
        print("  [4] Rellenar con la moda de la columna")
        print("  [5] Rellenar con un valor constante")
        print("  [6] Volver al menú principal")

        opcion = int(input("Seleccione una opción: "))
        
        # Elimina las filas que contienen los valores  
        if opcion == 1: 
            self.datos.dropna(subset=seleccionadas, inplace=True)
            print("Filas con valores faltantes eliminadas correctamente")
        
        # Rellena los valores con la media, la mediana y la moda en columnas numéricas
        elif opcion == 2:
            self.datos.fillna(self.datos.select_dtypes(include=['number']).mean(), inplace=True)
            print("Valores faltantes rellenados con la media de cada columna")
        elif opcion == 3:
            self.datos.fillna(self.datos.select_dtypes(include=['number']).median(), inplace=True)
            print("Valores faltantes rellenados con la mediana de cada columna")
        elif opcion == 4:
            self.datos.fillna(self.datos.select_dtypes(include=['number']).mode().iloc[0], inplace=True)
            print("Valores faltantes rellenados con la moda de cada columna")

        # Rellena los valores con un número  específico
        elif opcion == 5:
            valor = int(input("Ingrese un valor numérico para reemplazar los valores faltantes: "))
            self.datos.fillna(float(valor), inplace=True)
            print(f"Valores faltantes reemplazados con el valor {valor}")
        
        elif opcion == 6:
            return
        else:
            print("Opción inválida.")
            return
        
        
        self.paso = 2.3
        
    
    # Transformación de datos categóricos
    def opcion2_transformar_categoricos(self):

        # Filtra las columnas categóricas dentro de las features seleccionadas
        categoricos = [columna for columna in self.features if self.datos[columna].dtype == 'object']

        # Si no hay, informa de ello
        if not categoricos:
            print("\n=============================")
            print("Transformación de Datos Categóricos")
            print("=============================")
            print("No se han detectado columnas categóricas en las variables de entrada seleccionadas.")
            print("No es necesario aplicar ninguna transformación")
            self.paso = 2.4
            return
        
        # Muestra las columnas detectadas
        print("\n=============================")
        print("Transformación de Datos Categóricos")
        print("=============================")
        print("Se han detectado columnas categóricas en las variables de entrada seleccionadas:")
        for columna in categoricos:
            print(f"  - {columna}")
        
        # Opciones de transformación
        print("\nSeleccione una estrategia de transformación:")
        print("  [1] One-Hot Encoding (genera nuevas columnas binarias)")
        print("  [2] Label Encoding (convierte categorías a números enteros)")
        print("  [3] Volver al menú principal")  

        opcion = int(input("Seleccione una opción:"))

        if opcion == 1: # Crea nuevas columnas binarias para cada categoría
            self.datos = pd.get_dummies(self.datos, columns = categoricos)
            print("Transformación completada con One-Hot Encoding")

        elif opcion == 2: # Asigna un número entero a cada categoría
            etiqueta = LabelEncoder()
            
            for columna in categoricos:
                self.datos[columna] = self.datos[columna].astype(str)
                self.datos[columna] = etiqueta.fit_transform(self.datos[columna])
            print("Transformación completada con Label Encoding")

        elif opcion == 3:
            return
        
        else:
            print("Opción inválida")
            return
        
        self.paso = 2.4

    def opcion2_normalizar_numericas(self):
        # Filtra las columnas numéricas dentro de las features seleccionadas
        numericas = [columna for columna in self.features if columna in self.datos.columns and self.datos[columna].dtype in ['int64', 'float64']]
        
        # Si no hay, informa de ello
        if not numericas:
            print("\n=============================")
            print("Normalización y Escalado")
            print("=============================")
            print("No se han detectado columnas numéricas en las variables de entrada seleccionadas.")
            print("No es necesario aplicar ninguna normalización.")
            return
        
        # Muestra las columnas detectadas
        print("\n=============================")
        print("Normalización y Escalado")
        print("=============================")
        print("Se han detectado columnas numéricas en las variables de entrada seleccionadas:")
        for columna in numericas:
            print(f" - {columna}")
        
        # Opciones de normalización
        print("\nSeleccione una estrategia de normalización:")
        print(" [1] Min-Max Scaling (escala valores entre 0 y 1)")
        print(" [2] Z-score Normalization (media 0, desviación estándar 1)")
        print(" [3] Volver al menú principal")
        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1:
            scaler = MinMaxScaler()
            self.datos[numericas] = scaler.fit_transform(self.datos[numericas])
            print("Normalización completada con Min-Max Scaling.")
        
        elif opcion == 2:
            scaler = StandardScaler()
            self.datos[numericas] = scaler.fit_transform(self.datos[numericas])
            print("Normalización completada con Z-score Normalization.")
        
        elif opcion == 3:
            return
        
        else:
            print("Opción inválida")
            return
        
        self.paso = 2.5 
        
    

