import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import numpy as np
import os
import io
import sqlite3
import matplotlib
matplotlib.use('Agg')  # Usar backend sin ventanas para las pruebas

# Importar el módulo manejodatos
from manejodatos import Datos

class TestDatos(unittest.TestCase):
    
    def setUp(self):
        # Configuración común para las pruebas
        self.columnas_ejemplo = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 
                                'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
        
        # Ruta a los archivos de datos reales para pruebas
        self.csv_path = 'titanic_survival.csv'  
        self.excel_path = 'titanic_survival.xlsx'  
        self.sqlite_path = 'titanic_survival.db'  
        
        # Crear un DataFrame de ejemplo para cuando no existan los archivos de datos
        self.datos_ejemplo = pd.DataFrame({
            'PassengerId': [1, 2, 3, 4, 5],
            'Survived': [0, 1, 1, 0, 1],
            'Pclass': [3, 1, 3, 1, 2],
            'Name': ['Braund, Mr. Owen Harris', 'Cumings, Mrs. John Bradley', 'Heikkinen, Miss. Laina', 
                    'Futrelle, Mrs. Jacques Heath', 'Allen, Mr. William Henry'],
            'Sex': ['male', 'female', 'female', 'female', 'male'],
            'Age': [22.0, 38.0, 26.0, 35.0, np.nan],
            'SibSp': [1, 1, 0, 1, 0],
            'Parch': [0, 0, 0, 0, 0],
            'Ticket': ['A/5 21171', 'PC 17599', 'STON/O2. 3101282', '113803', '373450'],
            'Fare': [7.25, 71.2833, 7.925, 53.1, 8.05],
            'Cabin': [np.nan, 'C85', np.nan, 'C123', np.nan],
            'Embarked': ['S', 'C', 'S', 'S', 'S']
        })
        
        # Verificar si los archivos existen para las pruebas
        self.files_exist = (
            os.path.exists(self.csv_path) and 
            os.path.exists(self.excel_path) and 
            os.path.exists(self.sqlite_path)
        )
        
        # Si existen, cargar los datos reales
        if self.files_exist:
            try:
                self.datos_reales = pd.read_csv(self.csv_path)
            except Exception:
                self.datos_reales = self.datos_ejemplo
        else:
            self.datos_reales = self.datos_ejemplo
    
    @patch('menu.mostrar_menu', return_value="5")  # Simular selección de salir
    @patch('menu.cerrar')
    def test_init_y_proceso(self, mock_cerrar, mock_menu):
        # Probar inicialización de Datos y el método proceso
        with patch.object(Datos, 'proceso') as mock_proceso:
            datos = Datos()
            
            # Verificar que los atributos se inicializan correctamente
            self.assertIsNone(datos.ruta)
            self.assertIsNone(datos.datos)
            self.assertEqual(datos.features, [])
            self.assertIsNone(datos.targets)
            self.assertEqual(datos.paso, 1)
            self.assertFalse(datos.preprocesado)
            
            # Verificar que proceso fue llamado
            mock_proceso.assert_called_once()
    
    @patch('os.path.exists', return_value=True)
    @patch('menu.mostrar_datos')
    def test_opcion1_carga_csv(self, mock_mostrar, mock_exists):
        # Probar opción1_carga con un archivo CSV
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            
            # Determinar el archivo de prueba
            csv_file = self.csv_path if self.files_exist else 'titanic.csv'
            
            # Mockear la lectura del CSV
            with patch('pandas.read_csv', return_value=self.datos_reales) as mock_read_csv:
                with patch('menu.cargar_datos', return_value=(1, csv_file)):
                    datos.opcion1_carga()
                    
                    # Verificar que los atributos se actualizan correctamente
                    self.assertEqual(datos.paso, 2)
                    self.assertEqual(datos.ruta, csv_file)
                    mock_read_csv.assert_called_once_with(csv_file)
    
    @patch('menu.seleccion_terminal', return_value=(['PassengerId', 'Pclass', 'Age'], 'Survived'))
    def test_opcion2_selector_columnas(self, mock_seleccion):
        # Probar opción2_selector_columnas
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales
            datos.opcion2_selector_columnas()
            
            # Verificar que los atributos se actualizan correctamente
            self.assertEqual(datos.features, ['PassengerId', 'Pclass', 'Age'])
            self.assertEqual(datos.targets, 'Survived')
            self.assertEqual(datos.paso, 2.2)
    
    @patch('builtins.print')
    def test_opcion2_manejo_nulos(self, mock_print):
        # Probar opción2_manejo_nulos
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales.copy()
            
            # Asegurarse de que haya algunas columnas con NaN para la prueba
            datos.datos.loc[0, 'Age'] = np.nan
            
            datos.features = ['PassengerId', 'Pclass', 'Age']
            datos.targets = 'Survived'
            datos.paso = 2.2
            
            # Guardar el número de filas antes
            filas_antes = len(datos.datos)
            
            # Simular la selección de "eliminar filas con valores faltantes"
            with patch('builtins.input', return_value="1"):
                datos.opcion2_manejo_nulos()
                
                # Verificar que se han eliminado las filas con nulos
                if 'Age' in datos.datos.columns:
                    self.assertTrue(datos.datos['Age'].notna().all())
                self.assertEqual(datos.paso, 2.3)
    
    @patch('builtins.print')
    def test_opcion2_transformar_categoricos(self, mock_print):
        # Probar opción2_transformar_categoricos
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales.copy()
            
            # Asegurarse de que haya columnas categóricas
            if 'Sex' not in datos.datos.columns:
                datos.datos['Sex'] = ['male', 'female', 'male']
            if 'Embarked' not in datos.datos.columns:
                datos.datos['Embarked'] = ['S', 'C', 'Q']
            
            datos.features = ['Sex', 'Embarked']
            datos.targets = 'Survived' if 'Survived' in datos.datos.columns else datos.datos.columns[0]
            datos.paso = 2.3
            
            # Simular la selección de "Label Encoding"
            with patch('builtins.input', return_value="2"):
                datos.opcion2_transformar_categoricos()
                
                # Verificar que las columnas categóricas fueron transformadas
                self.assertEqual(datos.datos['Sex'].dtype, 'int64')
                self.assertEqual(datos.datos['Embarked'].dtype, 'int64')
                self.assertEqual(datos.paso, 2.4)
    
    @patch('builtins.print')
    def test_opcion2_normalizar_numericas(self, mock_print):
        # Probar opción2_normalizar_numericas
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales.copy()
            
            # Asegurarse de que haya columnas numéricas
            columnas_num = [col for col in datos.datos.columns if datos.datos[col].dtype in ['int64', 'float64']]
            if not columnas_num:
                datos.datos['Age'] = [22.0, 38.0, 26.0]
                datos.datos['Fare'] = [7.25, 71.28, 7.92]
                columnas_num = ['Age', 'Fare']
            
            datos.features = columnas_num[:2]  # Tomar las dos primeras columnas numéricas
            datos.targets = 'Survived' if 'Survived' in datos.datos.columns else datos.datos.columns[0]
            datos.paso = 2.4
            
            # Reemplazar NaN para evitar errores
            for col in datos.features:
                if datos.datos[col].isnull().any():
                    datos.datos[col].fillna(datos.datos[col].mean(), inplace=True)
            
            # Simular la selección de "Min-Max Scaling"
            with patch('builtins.input', return_value="1"):
                datos.opcion2_normalizar_numericas()
                
                # Verificar que las columnas numéricas fueron normalizadas
                for col in datos.features:
                    self.assertTrue((datos.datos[col] >= 0).all() and (datos.datos[col] <= 1).all())
                self.assertEqual(datos.paso, 2.5)
        print(datos.datos[col].min(), datos.datos[col].max())  # Ver los valores extremos
        self.assertTrue((datos.datos[col] >= 0).all() and (datos.datos[col] <= 1).all())        
    
    @patch('builtins.print')
    def test_opcion2_manejo_atipicos(self, mock_print):
        # Probar opción2_manejo_atipicos
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            
            # Crear datos con valores atípicos
            df_atipicos = pd.DataFrame({
                'col1': [1, 2, 3, 4, 100],  # 100 es un valor atípico
                'col2': [10, 20, 30, 40, 50]
            })
            datos.datos = df_atipicos
            datos.features = ['col1', 'col2']
            datos.targets = 'col2'
            datos.paso = 2.5
            
            # Simular la selección de "mantener valores atípicos"
            with patch('builtins.input', return_value="3"):
                datos.opcion2_manejo_atipicos()
                
                # Verificar que el paso se actualiza
                self.assertEqual(datos.paso, 3)
    
    @patch('builtins.print')
    @patch('pandas.DataFrame.describe', return_value="Resumen estadístico simulado")
    def test_opcion3_visualizar_datos(self, mock_describe, mock_print):
        # Probar opción3_visualizar_datos
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales.copy()
            
            # Asegurarse de que haya columnas numéricas
            columnas_num = [col for col in datos.datos.columns if datos.datos[col].dtype in ['int64', 'float64']]
            if not columnas_num:
                datos.datos['Age'] = [22.0, 38.0, 26.0]
                datos.datos['Fare'] = [7.25, 71.28, 7.92]
                columnas_num = ['Age', 'Fare']
            
            datos.features = columnas_num[:2]  # Tomar las dos primeras columnas numéricas
            datos.targets = 'Survived' if 'Survived' in datos.datos.columns else datos.datos.columns[0]
            datos.paso = 3
            
            # Reemplazar NaN para evitar errores
            for col in datos.features:
                if datos.datos[col].isnull().any():
                    datos.datos[col].fillna(datos.datos[col].mean(), inplace=True)
            
            # Simular la selección de resumen estadístico
            with patch('builtins.input', return_value="1"):
                datos.opcion3_visualizar_datos()
                
                # Verificar que el paso se actualiza
                self.assertEqual(datos.paso, 4)
    
    @patch('builtins.print')
    @patch('pandas.DataFrame.to_csv')
    def test_opcion4_exportar_datos(self, mock_to_csv, mock_print):
        # Probar opción4_exportar_datos
        with patch.object(Datos, 'proceso'):
            datos = Datos()
            datos.datos = self.datos_reales.copy()
            datos.paso = 4
            
            # Simular la selección de CSV y nombre de archivo
            with patch('builtins.input', side_effect=["1", "test_export"]):
                datos.opcion4_exportar_datos()
                
                # Verificar que to_csv fue llamado con los argumentos correctos
                mock_to_csv.assert_called_once_with('test_export.csv', index=False)
                self.assertEqual(datos.paso, 5)
    
    # Añadimos un método tearDown para limpiar después de las pruebas
    def tearDown(self):
        # Limpiar recursos o archivos temporales si es necesario
        pass

if __name__ == '__main__':
    unittest.main()

