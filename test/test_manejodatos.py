import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
from sklearn.preprocessing import  StandardScaler
import pandas as pd
import numpy as np
import io

# Agregar el directorio principal al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

with patch('manejodatos.Datos.proceso'):
    from manejodatos import Datos

class TestDatos(unittest.TestCase):
    # Creamos un DataFrame de prueba con la estructura proporcionada
    def setUp(self):
        self.test_data = pd.DataFrame({
            'PassengerId': [1, 2, 3, 4, 5],
            'Survived': [0, 1, 1, 1, 0],
            'Pclass': [3, 1, 3, 1, 3],
            'Name': ['Braund, Mr. Owen Harris', 'Cumings, Mrs. John Bradley (Florence Briggs Thayer)', 
                    'Heikkinen, Miss. Laina', 'Futrelle, Mrs. Jacques Heath (Lily May Peel)', 'Allen, Mr. William Henry'],
            'Sex': ['male', 'female', 'female', 'female', 'male'],
            'Age': [22, 38, 26, 35, np.nan],
            'SibSp': [1, 1, 0, 1, 0],
            'Parch': [0, 0, 0, 0, 0],
            'Ticket': ['A/5 21171', 'PC 17599', 'STON/O2. 3101282', '113803', '373450'],
            'Fare': [7.25, 71.28, 7.92, 53.10, 8.05],
            'Cabin': [np.nan, 'C85', np.nan, 'C123', np.nan],
            'Embarked': ['S', 'C', 'S', 'S', 'S']
        })

    # Probar la inicialización de los datos    
    def test_init(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
            
        # Verificar que se inicializa correctamente
        self.assertIsNone(datos_obj.ruta)
        self.assertIsNone(datos_obj.datos)
        self.assertEqual(datos_obj.features, [])
        self.assertIsNone(datos_obj.targets)
        self.assertEqual(datos_obj.paso, 1)
        self.assertFalse(datos_obj.preprocesado)
    
    # Cargar un archivo CSV
    def test_opcion1_carga_csv(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configuración de mocks para simular la carga
        with patch('manejodatos.cargar_datos', return_value=(1, 'test.csv')), \
             patch('os.path.exists', return_value=True), \
             patch('pandas.read_csv', return_value=self.test_data), \
             patch('manejodatos.mostrar_datos') as mock_mostrar_datos:
            
            # Ejecutar la función
            datos_obj.opcion1_carga()
            
        # Verificaciones
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'test.csv')
        self.assertIsNotNone(datos_obj.datos)
        mock_mostrar_datos.assert_called_once()
    
    # Carga de un archivo excel
    def test_opcion1_carga_excel(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configuración de mocks para simulación
        with patch('manejodatos.cargar_datos', return_value=(2, 'test.xlsx')), \
             patch('os.path.exists', return_value=True), \
             patch('pandas.read_excel', return_value=self.test_data), \
             patch('manejodatos.mostrar_datos') as mock_mostrar_datos:
            
            # Ejecutar la función 
            datos_obj.opcion1_carga()
            
        # Verificaciones
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'test.xlsx')
        self.assertIsNotNone(datos_obj.datos)
        mock_mostrar_datos.assert_called_once()
    
    # Carga de un archivo en una base SQlite
    def test_opcion1_carga_sqlite(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Mock para la conexión a SQLite
        mock_conn = MagicMock()
        
        # Configuración de mocks para simulación
        with patch('manejodatos.cargar_datos', return_value=(3, 'test.sqlite')), \
             patch('os.path.exists', return_value=True), \
             patch('sqlite3.connect', return_value=mock_conn), \
             patch('pandas.read_sql') as mock_read_sql, \
             patch('builtins.input', return_value='1'), \
             patch('manejodatos.mostrar_datos') as mock_mostrar_datos:
            
            # Configurar el comportamiento del mock read_sql
            mock_read_sql.side_effect = [
                pd.DataFrame({'name': ['passengers']}),  
                self.test_data  
            ]
            
            # Ejecutar la función 
            datos_obj.opcion1_carga()
            
        # Verificaciones
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'test.sqlite')
        self.assertIsNotNone(datos_obj.datos)
        mock_mostrar_datos.assert_called_once()
    
    # Carga de un archivo inexistente
    def test_carga_archivo_no_valido(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configuración de mock para simulación
        with patch('manejodatos.cargar_datos', return_value=(1, 'archivo_inexistente.csv')), \
             patch('os.path.exists', return_value=False), \
             patch('builtins.print') as mock_print:
            
            # Ejecutar la función 
            datos_obj.opcion1_carga()
            
        # Verificar que se mostró el mensaje de error
        mock_print.assert_any_call("Archivo no válido, inténtelo de nuevo")
    
    # Cargar archivo con una extensión incorrecta
    def test_carga_extension_incorrecta(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configuración de mock para simulación
        with patch('manejodatos.cargar_datos', return_value=(1, 'archivo.xlsx')), \
             patch('os.path.exists', return_value=True), \
             patch('builtins.print') as mock_print:
            
            # Ejecutar la función 
            datos_obj.opcion1_carga()
            
        # Verificar que se mostró el mensaje de error
        mock_print.assert_any_call('Archivo inválido: el tipo no coincide con la opción seleccionada')
    
    # Seleccionar columnas
    def test_selector_columnas(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto
        datos_obj.datos = self.test_data
        datos_obj.paso = 2
        
        # Simulación
        with patch('manejodatos.seleccion_terminal', return_value=(['Age', 'Sex', 'Pclass'], 'Survived')):
            datos_obj.opcion2_selector_columnas()
        
        # Verificaciones
        self.assertEqual(datos_obj.features, ['Age', 'Sex', 'Pclass'])
        self.assertEqual(datos_obj.targets, 'Survived')
        self.assertEqual(datos_obj.paso, 2.2)
    
    # Manejar valore nulos cuando no hay nulos
    def test_manejo_nulos_sin_nulos(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto
        df_sin_nulos = self.test_data.copy()
        df_sin_nulos['Age'].fillna(25, inplace=True)
        df_sin_nulos['Cabin'].fillna('Unknown', inplace=True)
        datos_obj.datos = df_sin_nulos
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Ejecutar la función 
        with patch('builtins.print') as mock_print:
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se informó que no hay valores nulos
        mock_print.assert_any_call("No se han detectado valores faltantes en las columnas seleccionadas.")
        self.assertEqual(datos_obj.paso, 2.3)
    
    # Existen valores nulos: eliminar filas
    def test_manejo_nulos_eliminar_filas(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se eliminaron las filas 
        self.assertEqual(len(datos_obj.datos), 4)  
        self.assertEqual(datos_obj.paso, 2.3)
    
    # Existen valores nulos: rellenar con la media
    def test_manejo_nulos_rellenar_media(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto con datos 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Calcular la media de Age
        media_age = datos_obj.datos['Age'].mean()
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se rellenaron con la media
        self.assertTrue(datos_obj.datos['Age'].notna().all())  
        self.assertEqual(datos_obj.datos.loc[4, 'Age'], media_age)  
        self.assertEqual(datos_obj.paso, 2.3)
    
    # Transformar datos categóricos: One-Hot Encoding
    def test_transformar_categoricos_one_hot(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.3
        datos_obj.features = ['Sex', 'Pclass', 'Embarked']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_transformar_categoricos()
        
        # Verificar que se crearon nuevas columnas para las categorías
        self.assertIn('Sex_female', datos_obj.datos.columns)
        self.assertIn('Sex_male', datos_obj.datos.columns)
        self.assertIn('Embarked_C', datos_obj.datos.columns)
        self.assertIn('Embarked_S', datos_obj.datos.columns)
        self.assertEqual(datos_obj.paso, 2.4)
    
    # Transformar datos categóricos: Label Encoding
    def test_transformar_categoricos_label_encoding(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.3
        datos_obj.features = ['Sex', 'Embarked']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_transformar_categoricos()
        
        # Verificar que las columnas categóricas ahora son numéricas
        self.assertTrue(pd.api.types.is_numeric_dtype(datos_obj.datos['Sex']))
        self.assertTrue(pd.api.types.is_numeric_dtype(datos_obj.datos['Embarked']))
        self.assertEqual(datos_obj.paso, 2.4)
    
    # Normalizar columnas numéricas: Min-Max Scaling
    def test_normalizar_numericas_min_max(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_normalizar_numericas()
        
        # Verificar que los valores están normalizados entre 0 y 1
        for col in ['Fare', 'Pclass']:  # Excluir Age que tiene NaN
            self.assertTrue((datos_obj.datos[col] >= 0).all() and (datos_obj.datos[col] <= 1).all())
        
        self.assertEqual(datos_obj.paso, 2.5)
    
    # Normalizar columnas numéricas: Z-score
    def test_normalizar_numericas_z_score(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        # Rellenar valores nulos para evitar problemas con la normalización
        datos_obj.datos['Age'].fillna(datos_obj.datos['Age'].mean(), inplace=True)
        datos_obj.paso = 2.4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 2 
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            scaler = StandardScaler()
            expected_transformed = scaler.fit_transform(datos_obj.datos[['Age', 'Fare', 'Pclass']])
            
            # Llamar a la función
            datos_obj.opcion2_normalizar_numericas()
        
        actual_transformed = datos_obj.datos[['Age', 'Fare', 'Pclass']].values
        
        # Verificar que las transformaciones son similares 
        for i in range(len(expected_transformed)):
            for j in range(len(expected_transformed[i])):
                self.assertTrue(abs(actual_transformed[i][j] - expected_transformed[i][j]) < 1e-5)
        
        self.assertEqual(datos_obj.paso, 2.5)
    
    # Manejo de valores atípicos: Eliminar filas
    def test_manejo_atipicos_eliminar_filas(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Crear datos con valores atípicos
        test_data_outliers = self.test_data.copy()
        test_data_outliers.loc[0, 'Fare'] = 1000.0  
        
        # Configurar el objeto 
        datos_obj.datos = test_data_outliers
        datos_obj.paso = 2.5
        datos_obj.features = ['Fare', 'Age', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_manejo_atipicos()
        
        # Verificar que se eliminó la fila con el valor atípico
        self.assertFalse((datos_obj.datos['Fare'] == 1000.0).any())
        self.assertEqual(datos_obj.paso, 3)
    
    # Manejo de valores atípicos: Reemplazar con la mediana
    def test_manejo_atipicos_reemplazar_mediana(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Crear datos con valores atípicos
        test_data_outliers = self.test_data.copy()
        test_data_outliers.loc[0, 'Fare'] = 1000.0  # Valor atípico
        
        # Configurar el objeto 
        datos_obj.datos = test_data_outliers
        datos_obj.paso = 2.5
        datos_obj.features = ['Fare', 'Age', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Calcular la mediana
        mediana_fare = test_data_outliers['Fare'].median()
        
        # Simular input del usuario para seleccionar opción
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_manejo_atipicos()
        
        # Verificar que el valor atípico fue reemplazado por la mediana
        self.assertFalse((datos_obj.datos['Fare'] == 1000.0).any())
        self.assertEqual(datos_obj.datos.loc[0, 'Fare'], mediana_fare)
        self.assertEqual(datos_obj.paso, 3)
    
    # Visualizar datos: Resumen estadístico
    def test_visualizar_datos_resumen_estadistico(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 3
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='1'), patch('builtins.print') as mock_print:
            datos_obj.opcion3_visualizar_datos()
        
        # Verificar que se mostró un resumen estadístico
        mock_print.assert_any_call("\nResumen estadístico de las variables seleccionadas:")
        self.assertEqual(datos_obj.paso, 4)
    
    # Visualizar datos: Mostrar histogramas
    @patch('matplotlib.pyplot.show')
    def test_visualizar_datos_histogramas(self, mock_show):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 3
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 
        with patch('builtins.input', return_value='2'):
            datos_obj.opcion3_visualizar_datos()
        
        # Verificar que se generaron histogramas
        mock_show.assert_called_once()
        self.assertEqual(datos_obj.paso, 4)
    
    # Exportar datos: Archivo CSV
    def test_exportar_datos_csv(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        with patch('pandas.DataFrame.to_csv') as mock_to_csv, \
             patch('builtins.input', side_effect=['1', 'datos_exportados']), \
             patch('builtins.print') as mock_print:
            datos_obj.opcion4_exportar_datos()
        
        # Verificar que se exportó a CSV
        mock_to_csv.assert_called_once_with('datos_exportados.csv', index=False)
        mock_print.assert_any_call('Datos exportados correctamente como "datos_exportados.csv".')
        self.assertEqual(datos_obj.paso, 5)
    
    # Exportar datos: Archivo excel
    def test_exportar_datos_excel(self):
        with patch('manejodatos.Datos.proceso'):
            datos_obj = Datos()
        
        # Configurar el objeto 
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        with patch('pandas.DataFrame.to_excel') as mock_to_excel, \
             patch('builtins.input', side_effect=['2', 'datos_exportados']), \
             patch('builtins.print') as mock_print:
            datos_obj.opcion4_exportar_datos()
        
        # Verificar que se exportó a Excel
        mock_to_excel.assert_called_once_with('datos_exportados.xlsx', index=False)
        mock_print.assert_any_call('Datos exportados correctamente como "datos_exportados.xlsx".')
        self.assertEqual(datos_obj.paso, 5)

if __name__ == '__main__':
    unittest.main()
