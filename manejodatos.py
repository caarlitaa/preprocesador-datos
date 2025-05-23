
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


    def proceso(self, opcion = None): 
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
            
            elif opcion == "3" and self.paso >= 3: # Visualizar datos antes y después del preprocesado
                self.opcion3_visualizar_datos()
                
            elif opcion == "4" and self.paso >= 4: # Exportar los datos
                self.opcion4_exportar_datos()
            
            elif opcion == "5": # Cerrar la app
                cerrar()
            
            else:
                print("Opción inválida.")

    
    # Carga los datos según el  formato
    def opcion1_carga(self): 
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
                    conexion = sqlite3.connect(ruta)
                    consulta = "SELECT name FROM sqlite_master WHERE type='table';"
                    tablas = pd.read_sql(consulta, conexion) 
                    
                    if tablas.empty:
                        raise ValueError("No se encontraron tablas disponibles.")
                    
                    # Muestra las tablas disponibles y solicita la selección de una
                    print("Tablas disponibles en la base de datos:")
                    for i, tabla in enumerate(tablas['name'], 1):
                        print(f"  [{i}] {tabla}")

                    seleccion = input("Seleccione una tabla: ") 
                    if not seleccion.isdigit() or not (1 <= int(seleccion) <= len(tablas)):
                        raise ValueError("Selección inválida.")
                    
                    # Obtiene el nombre y carga sus datos
                    tabla_seleccionada = tablas.iloc[int(seleccion) - 1]['name']
                    self.datos = pd.read_sql(f"SELECT * FROM {tabla_seleccionada}", conexion)
                    conexion.close()
                    
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
            self.datos = pd.get_dummies(self.datos, columns = categoricos, dtype = int)
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
            print("Normalización completada con Min-Max Scaling")
        
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
        
    

    def opcion2_manejo_atipicos(self):
        # Seleccionamos las columnas numéricas dentro de las variables de entrada
        numericas = [columna for columna in self.features if columna in self.datos.columns and self.datos[columna].dtype in ['int64', 'float64']]
        
        if not numericas:
            print("\n=============================")
            print("Detección y Manejo de Valores Atípicos")
            print("=============================")
            print("No se han detectado columnas numéricas en las variables de entrada seleccionadas.")
            return
        
        valores_atipicos = {} # Almacenamos la cantidad de valores atípicos por columna
        
        # Identificamos valores atípicos utilizando el rango intercuartílico (IQR)
        for columna in numericas:
            Q1 = self.datos[columna].quantile(0.25)
            Q3 = self.datos[columna].quantile(0.75)
            IQR = Q3 - Q1
            # Contamos los atípicos fuera del ranfo permitido
            atipicos = ((self.datos[columna] < (Q1 - 1.5 * IQR)) | (self.datos[columna] > (Q3 + 1.5 * IQR))).sum()
            if atipicos > 0:
                valores_atipicos[columna] = atipicos
        
        # Si no se detecta ninguno, informa de ello
        if not valores_atipicos:
            print("\n=============================")
            print("Detección y Manejo de Valores Atípicos")
            print("=============================")
            print("No se han detectado valores atípicos en las columnas seleccionadas.")
            self.paso = 3
            return
        
        # Mostramos las columnas y la cantidad detectada
        print("\n=============================")
        print("Detección y Manejo de Valores Atípicos")
        print("=============================")
        print("Se han detectado valores atípicos en las siguientes columnas numéricas seleccionadas:")
        for columna, cantidad in valores_atipicos.items():
            print(f"  - {columna}: {cantidad} valores atípicos detectados")
        
        # Opciones para el manejo de los valores
        print("\nSeleccione una estrategia para manejar los valores atípicos:")
        print("  [1] Eliminar filas con valores atípicos")
        print("  [2] Reemplazar valores atípicos con la mediana de la columna")
        print("  [3] Mantener valores atípicos sin cambios")
        print("  [4] Volver al menú principal")
        
        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1: # Eliminar filas 
            for columna in valores_atipicos.keys():
                Q1 = self.datos[columna].quantile(0.25)
                Q3 = self.datos[columna].quantile(0.75)
                IQR = Q3 - Q1
                self.datos = self.datos[(self.datos[columna] >= (Q1 - 1.5 * IQR)) & (self.datos[columna] <= (Q3 + 1.5 * IQR))]
            print("Filas con valores atípicos eliminadas correctamente.")
        
        elif opcion == 2: # Reemplazar con la mediana de la columna
            for columna in valores_atipicos.keys():
                mediana = self.datos[columna].median()
                Q1 = self.datos[columna].quantile(0.25)
                Q3 = self.datos[columna].quantile(0.75)
                IQR = Q3 - Q1
                self.datos.loc[(self.datos[columna] < (Q1 - 1.5 * IQR)) | (self.datos[columna] > (Q3 + 1.5 * IQR)), columna] = mediana
            print("Valores atípicos reemplazados con la mediana de cada columna.")
        
        elif opcion == 3: # Se mantienen los valores
            print("Valores atípicos mantenidos sin cambios.")
        
        elif opcion == 4:
            return
        
        else:
            print("Opción inválida.")
            return
        
        self.paso = 3
        


    def opcion3_visualizar_datos(self):
        print("\n=============================")
        print("Visualización de Datos")
        print("=============================")

        # Verifica si el preprocesado fue completado
        if self.paso < 3:
            print("No es posible visualizar los datos hasta que se complete el preprocesado.")
            print("Por favor, finalice el manejo de valores atípicos antes de continuar")
            return
        
        # Verificar que las columnas seleccionadas existen en el DataFrame
        columnas = [columna for columna in self.features if columna in self.datos.columns]
        if not columnas:
            print("No se encontraron columnas seleccionadas en los datos.")
            return

        # Opciones de visualización
        print("Seleccione qué tipo de visualización desea generar:")
        print("  [1] Resumen estadístico de las variables seleccionadas")
        print("  [2] Histogramas de variables numéricas")
        print("  [3] Gráficos de dispersión antes y después de la normalización")
        print("  [4] Heatmap de correlación de variables numéricas")
        print("  [5] Volver al menú principal")

        opcion = int(input("Seleccione una opción: "))
        
        if opcion == 1:  # Resumen estadísticos de las columnas seleccionadas
            print("\nResumen estadístico de las variables seleccionadas:")
            print("-------------------------------------------------------------------")
            print("Variable      | Media | Mediana | Desviación Est. | Mínimo | Máximo")
            print("-------------------------------------------------------------------")
            
            # Obtener estadísticas
            estadisticas = self.datos[columnas].describe().T  # Transpone para tener variables en filas
            
            # Imprimir cada fila
            for variable in estadisticas.index:
                media = round(estadisticas.loc[variable, 'mean'], 1)
                mediana = round(estadisticas.loc[variable, '50%'], 0)
                desv = round(estadisticas.loc[variable, 'std'], 1)
                minimo = round(estadisticas.loc[variable, 'min'], 0)
                maximo = round(estadisticas.loc[variable, 'max'], 0)
                
                print(f"{variable:<13} | {media:<5} | {mediana:<7} | {desv:<15} | {minimo:<6} | {maximo}")
        
        elif opcion == 2: # Histogramas para las columnas numéricas
            self.datos[columnas].hist(bins=20, figsize=(12, 8))
            plt.show()
        
        elif opcion == 3: # Gráficos de dispersión antes y después de la normalización
            for columna in columnas:
                if self.datos[columna].dtype in ['int64', 'float64']:
                    plt.figure(figsize=(6, 4))
                    plt.scatter(range(len(self.datos)), self.datos[columna], label=f"{columna} (original)", alpha=0.5)
                    plt.scatter(range(len(self.datos)), MinMaxScaler().fit_transform(self.datos[[columna]]), label=f"{columna} (normalizado)", alpha=0.5)
                    plt.legend()
                    plt.title(f"Comparación de {columna} antes y después de la normalización")
                    plt.show()
        
        elif opcion == 4: # Heatmap de la correlación entre variables numéricas
            plt.figure(figsize=(10, 6))
            sns.heatmap(self.datos[columnas].corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Heatmap de correlación de variables numéricas")
            plt.show()
        
        elif opcion == 5:
            return
        
        else:
            print("Opción inválida.")
            return

        self.paso = 4

    def opcion4_exportar_datos(self):
        print("\n=============================")
        print("Exportación de Datos")
        print("=============================")
    
    # Verifica si preprocesado y visualización fueron completados
        if self.paso < 4:
            print("No es posible exportar los datos hasta que se complete el preprocesado y la visualización.")
            print("Por favor, finalice todas las etapas antes de continuar")
            return

        # Opciones de exportación
        print("Seleccione el formato de exportación:")
        print("  [1] CSV (.csv)")
        print("  [2] Excel (.xlsx)")
        print("  [3] Volver al menú principal")

        opcion = int(input("Seleccione una opción: "))
        
        # Valida la opción
        if opcion not in [1, 2]:
            print("Opción inválida.")
            return
        
        # Solicita el nombre del archivo sin extensión
        nombre = input("Ingrese el nombre del archivo de salida (sin extensión): ")
        
        # Exporta los datos en el formato seleccionado
        if opcion == 1: # CSV
            archivo  = f"{nombre}.csv"
            self.datos.to_csv(archivo, index=False)
        
        elif opcion == 2: # Excel
            archivo= f"{nombre}.xlsx"
            self.datos.to_excel(archivo, index=False)
        
        elif opcion == 3:
            return
        print(f"Datos exportados correctamente como \"{archivo}\".")

        self.paso = 5