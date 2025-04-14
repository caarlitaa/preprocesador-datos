import os
import sys
import unittest
from unittest.mock import patch, MagicMock, call
import pandas as pd
import numpy as np
import io

# Agregar el directorio principal al path para poder importar los módulos
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Importamos después de configurar el path
from manejodatos import Datos

class TestDatos(unittest.TestCase):
    """Pruebas unitarias para la clase Datos en manejodatos.py"""
    
    def setUp(self):
        """Configuración inicial para las pruebas"""
        # Creamos un DataFrame de prueba con la estructura proporcionada
        self.test_data = pd.DataFrame({
            'PassengerId': [1, 2, 3, 4, 5],
            'Survived': [0, 1, 1, 0, 1],
            'Pclass': [3, 1, 3, 1, 2],
            'Name': ['Braund, Mr. Owen Harris', 'Cumings, Mrs. John Bradley (Florence Briggs Thayer)', 
                    'Heikkinen, Miss. Laina', 'Futrelle, Mrs. Jacques Heath (Lily May Peel)', 'Allen, Mr. William Henry'],
            'Sex': ['male', 'female', 'female', 'female', 'male'],
            'Age': [22.0, 38.0, 26.0, 35.0, np.nan],
            'SibSp': [1, 1, 0, 1, 0],
            'Parch': [0, 0, 0, 0, 0],
            'Ticket': ['A/5 21171', 'PC 17599', 'STON/O2. 3101282', '113803', '373450'],
            'Fare': [7.25, 71.2833, 7.925, 53.1, 8.05],
            'Cabin': [np.nan, 'C85', np.nan, 'C123', np.nan],
            'Embarked': ['S', 'C', 'S', 'S', 'S']
        })
        
        # Patch para menu.py y otras dependencias
        self.menu_patcher = patch('manejodatos.mostrar_menu')
        self.cerrar_patcher = patch('manejodatos.cerrar')
        self.cargar_datos_patcher = patch('manejodatos.cargar_datos')
        self.mostrar_datos_patcher = patch('manejodatos.mostrar_datos')
        self.seleccion_terminal_patcher = patch('manejodatos.seleccion_terminal')
        
        # Inicializamos los mocks
        self.mock_mostrar_menu = self.menu_patcher.start()
        self.mock_cerrar = self.cerrar_patcher.start()
        self.mock_cargar_datos = self.cargar_datos_patcher.start()
        self.mock_mostrar_datos = self.mostrar_datos_patcher.start()
        self.mock_seleccion_terminal = self.seleccion_terminal_patcher.start()
        
        # Configuración de comportamiento por defecto
        self.mock_mostrar_menu.side_effect = ["5"]  # Para salir inmediatamente
        
    def tearDown(self):
        """Limpieza después de cada prueba"""
        self.menu_patcher.stop()
        self.cerrar_patcher.stop()
        self.cargar_datos_patcher.stop()
        self.mostrar_datos_patcher.stop()
        self.seleccion_terminal_patcher.stop()
    
    @patch('pandas.read_csv')
    def test_opcion1_carga_csv(self, mock_read_csv):
        """Prueba la carga de un archivo CSV"""
        # Configurar mocks
        self.mock_cargar_datos.return_value = (1, 'datos_prueba.csv')
        mock_read_csv.return_value = self.test_data
        self.mock_mostrar_menu.side_effect = ["1", "5"]
        
        with patch('os.path.exists', return_value=True):
            datos_obj = Datos()
            
        # Verificaciones
        self.mock_cargar_datos.assert_called_once()
        mock_read_csv.assert_called_once_with('datos_prueba.csv')
        self.mock_mostrar_datos.assert_called_once()
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'datos_prueba.csv')
    
    @patch('pandas.read_excel')
    def test_opcion1_carga_excel(self, mock_read_excel):
        """Prueba la carga de un archivo Excel"""
        # Configurar mocks
        self.mock_cargar_datos.return_value = (2, 'datos_prueba.xlsx')
        mock_read_excel.return_value = self.test_data
        self.mock_mostrar_menu.side_effect = ["1", "5"]
        
        with patch('os.path.exists', return_value=True):
            datos_obj = Datos()
            
        # Verificaciones
        self.mock_cargar_datos.assert_called_once()
        mock_read_excel.assert_called_once_with('datos_prueba.xlsx')
        self.mock_mostrar_datos.assert_called_once()
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'datos_prueba.xlsx')
    
    @patch('sqlite3.connect')
    @patch('pandas.read_sql')
    def test_opcion1_carga_sqlite(self, mock_read_sql, mock_connect):
        """Prueba la carga de una base de datos SQLite"""
        # Configurar mocks
        self.mock_cargar_datos.return_value = (3, 'datos_prueba.sqlite')
        mock_connect.return_value = MagicMock()
        mock_read_sql.side_effect = [
            pd.DataFrame({'name': ['passengers']}),  # Tabla disponible
            self.test_data  # Datos de la tabla
        ]
        self.mock_mostrar_menu.side_effect = ["1", "5"]
        
        # Simular input del usuario para seleccionar tabla
        with patch('os.path.exists', return_value=True), patch('builtins.input', return_value='1'):
            datos_obj = Datos()
            
        # Verificaciones
        self.mock_cargar_datos.assert_called_once()
        mock_connect.assert_called_once_with('datos_prueba.sqlite')
        self.assertEqual(mock_read_sql.call_count, 2)
        self.mock_mostrar_datos.assert_called_once()
        self.assertEqual(datos_obj.paso, 2)
        self.assertEqual(datos_obj.ruta, 'datos_prueba.sqlite')
    
    def test_carga_archivo_no_valido(self):
        """Prueba con un archivo que no existe"""
        self.mock_cargar_datos.return_value = (1, 'archivo_no_existe.csv')
        self.mock_mostrar_menu.side_effect = ["1", "5"]
        
        with patch('os.path.exists', return_value=False), patch('builtins.print') as mock_print:
            datos_obj = Datos()
            
        # Verificar que se mostró el mensaje de error
        mock_print.assert_any_call("Archivo no válido, inténtelo de nuevo")
    
    def test_selector_columnas(self):
        """Prueba la selección de columnas"""
        # Configurar el objeto con datos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data
        datos_obj.paso = 2
        
        # Simular selección de columnas
        self.mock_seleccion_terminal.return_value = (['Age', 'Sex', 'Pclass'], 'Survived')
        
        # Ejecutar la función
        datos_obj.opcion2_selector_columnas()
        
        # Verificaciones
        self.mock_seleccion_terminal.assert_called_once_with(list(self.test_data.columns))
        self.assertEqual(datos_obj.features, ['Age', 'Sex', 'Pclass'])
        self.assertEqual(datos_obj.targets, 'Survived')
        self.assertEqual(datos_obj.paso, 2.2)
    
    def test_manejo_nulos_sin_nulos(self):
        """Prueba el manejo de valores nulos cuando no hay nulos"""
        # Configurar el objeto con datos sin valores nulos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        df_sin_nulos = self.test_data.copy()
        df_sin_nulos['Age'].fillna(25, inplace=True)
        df_sin_nulos['Cabin'].fillna('Unknown', inplace=True)
        datos_obj.datos = df_sin_nulos
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Ejecutar la función con un patch para print
        with patch('builtins.print') as mock_print:
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se informó que no hay valores nulos
        mock_print.assert_any_call("No se han detectado valores faltantes en las columnas seleccionadas.")
        self.assertEqual(datos_obj.paso, 2.3)
    
    def test_manejo_nulos_eliminar_filas(self):
        """Prueba eliminar filas con valores nulos"""
        # Configurar el objeto con datos que tienen valores nulos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 1 (eliminar filas)
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se eliminaron las filas con valores nulos
        self.assertEqual(len(datos_obj.datos), 4)  # 5 filas originales - 1 con Age nulo
        self.assertEqual(datos_obj.paso, 2.3)
    
    def test_manejo_nulos_rellenar_media(self):
        """Prueba rellenar valores nulos con la media"""
        # Configurar el objeto con datos que tienen valores nulos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.2
        datos_obj.features = ['Age', 'Sex', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Calcular la media de Age para comprobar después
        media_age = datos_obj.datos['Age'].mean()
        
        # Simular input del usuario para seleccionar opción 2 (rellenar con media)
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_manejo_nulos()
        
        # Verificar que se rellenaron los valores nulos con la media
        self.assertTrue(datos_obj.datos['Age'].notna().all())  # No debe haber NaN en Age
        self.assertEqual(datos_obj.datos.loc[4, 'Age'], media_age)  # El valor NaN fue reemplazado por la media
        self.assertEqual(datos_obj.paso, 2.3)
    
    def test_transformar_categoricos_one_hot(self):
        """Prueba la transformación de datos categóricos con One-Hot Encoding"""
        # Configurar el objeto con datos que tienen columnas categóricas
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.3
        datos_obj.features = ['Sex', 'Pclass', 'Embarked']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 1 (One-Hot Encoding)
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_transformar_categoricos()
        
        # Verificar que se crearon nuevas columnas para las categorías
        self.assertIn('Sex_female', datos_obj.datos.columns)
        self.assertIn('Sex_male', datos_obj.datos.columns)
        self.assertIn('Embarked_C', datos_obj.datos.columns)
        self.assertIn('Embarked_S', datos_obj.datos.columns)
        self.assertEqual(datos_obj.paso, 2.4)
    
    def test_transformar_categoricos_label_encoding(self):
        """Prueba la transformación de datos categóricos con Label Encoding"""
        # Configurar el objeto con datos que tienen columnas categóricas
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.3
        datos_obj.features = ['Sex', 'Embarked']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 2 (Label Encoding)
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_transformar_categoricos()
        
        # Verificar que las columnas categóricas ahora son numéricas
        self.assertTrue(pd.api.types.is_numeric_dtype(datos_obj.datos['Sex']))
        self.assertTrue(pd.api.types.is_numeric_dtype(datos_obj.datos['Embarked']))
        self.assertEqual(datos_obj.paso, 2.4)
    
    def test_normalizar_numericas_min_max(self):
        """Prueba la normalización de columnas numéricas con Min-Max Scaling"""
        # Configurar el objeto con datos que tienen columnas numéricas
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 2.4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 1 (Min-Max Scaling)
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_normalizar_numericas()
        
        # Verificar que los valores están normalizados entre 0 y 1
        for col in ['Age', 'Fare', 'Pclass']:
            if col in datos_obj.datos.columns:  # Age podría tener NaN
                valid_values = datos_obj.datos[col].dropna()
                self.assertTrue((valid_values >= 0).all() and (valid_values <= 1).all())
        
        self.assertEqual(datos_obj.paso, 2.5)
    
    def test_normalizar_numericas_z_score(self):
        """Prueba la normalización de columnas numéricas con Z-score"""
        # Configurar el objeto con datos que tienen columnas numéricas
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        # Rellenar valores NaN para evitar problemas con la normalización
        datos_obj.datos['Age'].fillna(datos_obj.datos['Age'].mean(), inplace=True)
        datos_obj.paso = 2.4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 2 (Z-score)
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_normalizar_numericas()
        
        # Verificar que los valores están normalizados (media cercana a 0 y desviación estándar cercana a 1)
        for col in ['Age', 'Fare', 'Pclass']:
            if col in datos_obj.datos.columns:
                self.assertTrue(abs(datos_obj.datos[col].mean()) < 1e-10)  # Media cercana a 0
                self.assertTrue(abs(datos_obj.datos[col].std() - 1.0) < 1e-10)  # Desviación estándar cercana a 1
        
        self.assertEqual(datos_obj.paso, 2.5)
    
    def test_manejo_atipicos_eliminar_filas(self):
        """Prueba eliminar filas con valores atípicos"""
        # Crear datos con valores atípicos
        test_data_outliers = self.test_data.copy()
        test_data_outliers.loc[0, 'Fare'] = 1000.0  # Valor atípico
        
        # Configurar el objeto con datos que tienen valores atípicos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = test_data_outliers
        datos_obj.paso = 2.5
        datos_obj.features = ['Fare', 'Age', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 1 (eliminar filas)
        with patch('builtins.input', return_value='1'), patch('builtins.print'):
            datos_obj.opcion2_manejo_atipicos()
        
        # Verificar que se eliminó la fila con el valor atípico
        self.assertFalse((datos_obj.datos['Fare'] == 1000.0).any())
        self.assertEqual(datos_obj.paso, 3)
    
    def test_manejo_atipicos_reemplazar_mediana(self):
        """Prueba reemplazar valores atípicos con la mediana"""
        # Crear datos con valores atípicos
        test_data_outliers = self.test_data.copy()
        test_data_outliers.loc[0, 'Fare'] = 1000.0  # Valor atípico
        
        # Configurar el objeto con datos que tienen valores atípicos
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = test_data_outliers
        datos_obj.paso = 2.5
        datos_obj.features = ['Fare', 'Age', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Calcular la mediana para comprobar después
        mediana_fare = test_data_outliers['Fare'].median()
        
        # Simular input del usuario para seleccionar opción 2 (reemplazar con mediana)
        with patch('builtins.input', return_value='2'), patch('builtins.print'):
            datos_obj.opcion2_manejo_atipicos()
        
        # Verificar que el valor atípico fue reemplazado por la mediana
        self.assertFalse((datos_obj.datos['Fare'] == 1000.0).any())
        self.assertEqual(datos_obj.datos.loc[0, 'Fare'], mediana_fare)
        self.assertEqual(datos_obj.paso, 3)
    
    def test_visualizar_datos_resumen_estadistico(self):
        """Prueba la visualización de resumen estadístico"""
        # Configurar el objeto con datos preprocesados
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 3
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 1 (resumen estadístico)
        with patch('builtins.input', return_value='1'), patch('builtins.print') as mock_print:
            datos_obj.opcion3_visualizar_datos()
        
        # Verificar que se mostró un resumen estadístico
        mock_print.assert_any_call("\nResumen estadístico de las variables seleccionadas:")
        self.assertEqual(datos_obj.paso, 4)
    
    @patch('matplotlib.pyplot.show')
    def test_visualizar_datos_histogramas(self, mock_show):
        """Prueba la visualización de histogramas"""
        # Configurar el objeto con datos preprocesados
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 3
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Simular input del usuario para seleccionar opción 2 (histogramas)
        with patch('builtins.input', return_value='2'):
            datos_obj.opcion3_visualizar_datos()
        
        # Verificar que se generaron histogramas
        mock_show.assert_called_once()
        self.assertEqual(datos_obj.paso, 4)
    
    def test_exportar_datos_csv(self):
        """Prueba la exportación de datos a CSV"""
        # Configurar el objeto con datos preparados para exportar
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Patch para to_csv y para el input del usuario
        with patch('pandas.DataFrame.to_csv') as mock_to_csv, \
             patch('builtins.input', side_effect=['1', 'datos_exportados']), \
             patch('builtins.print') as mock_print:
            datos_obj.opcion4_exportar_datos()
        
        # Verificar que se exportó a CSV
        mock_to_csv.assert_called_once_with('datos_exportados.csv', index=False)
        mock_print.assert_any_call('Datos exportados correctamente como "datos_exportados.csv".')
        self.assertEqual(datos_obj.paso, 5)
    
    def test_exportar_datos_excel(self):
        """Prueba la exportación de datos a Excel"""
        # Configurar el objeto con datos preparados para exportar
        self.mock_mostrar_menu.side_effect = ["5"]
        datos_obj = Datos()
        datos_obj.datos = self.test_data.copy()
        datos_obj.paso = 4
        datos_obj.features = ['Age', 'Fare', 'Pclass']
        datos_obj.targets = 'Survived'
        
        # Patch para to_excel y para el input del usuario
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
