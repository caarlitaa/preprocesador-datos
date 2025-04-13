import unittest
import os
import sys
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
from io import StringIO

# Añadimos el directorio padre al path para poder importar los módulos correctamente
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importamos el módulo a probar
from manejodatos import Datos

class TestDatos(unittest.TestCase):
    
    def setUp(self):
        """Configuración inicial para cada prueba"""
        # Creamos un DataFrame de prueba
        self.test_data = pd.DataFrame({
            'nombre': ['Ana', 'Juan', 'Pedro', 'Maria', None],
            'edad': [25, 30, None, 22, 40],
            'salario': [50000, 60000, 55000, None, 70000],
            'categoria': ['A', 'B', 'A', 'C', 'B'],
            'resultado': [1, 0, 1, 0, 1]
        })
        
        # Guardamos el DataFrame en formatos CSV y Excel para pruebas
        self.csv_path = os.path.join(os.path.dirname(__file__), 'test_data.csv')
        self.excel_path = os.path.join(os.path.dirname(__file__), 'test_data.xlsx')
        
        self.test_data.to_csv(self.csv_path, index=False)
        self.test_data.to_excel(self.excel_path, index=False)
    
    def tearDown(self):
        """Limpieza después de cada prueba"""
        # Eliminar archivos temporales
        if os.path.exists(self.csv_path):
            os.remove(self.csv_path)
        if os.path.exists(self.excel_path):
            os.remove(self.excel_path)
            
        # Eliminar cualquier archivo de exportación que se haya creado
        export_files = ['test_export.csv', 'test_export.xlsx']
        for file in export_files:
            if os.path.exists(file):
                os.remove(file)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cerrar')
    def test_proceso_cerrar(self, mock_cerrar, mock_menu):
        """Prueba para verificar que la opción 5 cierra la aplicación"""
        # Configuramos el mock para que devuelva "5" (cerrar)
        mock_menu.return_value = "5"
        
        datos = Datos()
        
        # Verificamos que se llamó a la función cerrar
        mock_cerrar.assert_called_once()
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.mostrar_datos')
    def test_opcion1_carga_csv(self, mock_mostrar_datos, mock_cargar_datos, mock_menu):
        """Prueba de carga de datos CSV"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "5"]  # Primero carga, luego cierra
        mock_cargar_datos.return_value = (1, self.csv_path)
        
        with patch('builtins.print') as mock_print:
            datos = Datos()
            
            # Verificamos que los datos se cargaron correctamente
            self.assertIsNotNone(datos.datos)
            self.assertEqual(datos.paso, 2)
            mock_mostrar_datos.assert_called_with(datos.datos, self.csv_path)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.mostrar_datos')
    def test_opcion1_carga_excel(self, mock_mostrar_datos, mock_cargar_datos, mock_menu):
        """Prueba de carga de datos Excel"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "5"]  # Primero carga, luego cierra
        mock_cargar_datos.return_value = (2, self.excel_path)
        
        with patch('builtins.print') as mock_print:
            datos = Datos()
            
            # Verificamos que los datos se cargaron correctamente
            self.assertIsNotNone(datos.datos)
            self.assertEqual(datos.paso, 2)
            mock_mostrar_datos.assert_called_with(datos.datos, self.excel_path)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    def test_opcion2_selector_columnas(self, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de selección de columnas"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['nombre', 'edad', 'salario', 'categoria'], 'resultado')
        
        datos = Datos()
        
        # Verificamos que las columnas se seleccionaron correctamente
        self.assertEqual(datos.features, ['nombre', 'edad', 'salario', 'categoria'])
        self.assertEqual(datos.targets, 'resultado')
        self.assertEqual(datos.paso, 2.2)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    def test_opcion2_manejo_nulos(self, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de manejo de valores nulos"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['nombre', 'edad', 'salario'], 'resultado')
        
        with patch('builtins.input', return_value='1'):  # Opción 1: Eliminar filas con nulos
            datos = Datos()
            
            # Verificamos que se eliminaron las filas con nulos
            self.assertFalse(datos.datos[['nombre', 'edad', 'salario', 'resultado']].isnull().any().any())
            self.assertEqual(datos.paso, 2.3)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    def test_opcion2_transformar_categoricos(self, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de transformación de datos categóricos"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "2.3", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['nombre', 'categoria'], 'resultado')
        
        # Para eliminar nulos y proceder a transformación categórica
        with patch('builtins.input', side_effect=['1', '2']):  # Eliminar nulos, Label Encoding
            datos = Datos()
            
            # Verificamos que la columna categórica está ahora en formato numérico
            self.assertTrue(datos.datos['categoria'].dtype in ['int64', 'float64'])
            self.assertEqual(datos.paso, 2.4)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    @patch('matplotlib.pyplot.show')
    def test_opcion2_normalizar_numericas(self, mock_plt_show, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de normalización de datos numéricos"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "2.3", "2.4", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['edad', 'salario'], 'resultado')
        
        # Para eliminar nulos, saltar transformación categórica y normalizar
        with patch('builtins.input', side_effect=['1', '3', '1']):  # Eliminar nulos, Volver, Min-Max
            datos = Datos()
            
            # Verificamos que los datos se normalizaron (entre 0 y 1)
            self.assertTrue((datos.datos['edad'] >= 0).all() and (datos.datos['edad'] <= 1).all())
            self.assertTrue((datos.datos['salario'] >= 0).all() and (datos.datos['salario'] <= 1).all())
            self.assertEqual(datos.paso, 2.5)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    def test_opcion2_manejo_atipicos(self, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de manejo de valores atípicos"""
        # Creamos datos con valores atípicos evidentes
        test_data_outliers = pd.DataFrame({
            'edad': [25, 30, 28, 22, 100],  # 100 es un valor atípico
            'salario': [50000, 60000, 55000, 58000, 500000],  # 500000 es un valor atípico
            'resultado': [1, 0, 1, 0, 1]
        })
        outliers_path = os.path.join(os.path.dirname(__file__), 'test_outliers.csv')
        test_data_outliers.to_csv(outliers_path, index=False)
        
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "2.3", "2.4", "2.5", "5"]
        mock_cargar_datos.return_value = (1, outliers_path)
        mock_seleccion.return_value = (['edad', 'salario'], 'resultado')
        
        try:
            # Para realizar todas las operaciones necesarias
            with patch('builtins.input', side_effect=['3', '3', '3', '2']):  # Varias ops y reemplazar atípicos
                datos = Datos()
                
                # Verificamos que los valores atípicos fueron manejados
                # En este caso, reemplazados por la mediana
                self.assertLess(datos.datos['edad'].max(), 100)
                self.assertLess(datos.datos['salario'].max(), 500000)
                self.assertEqual(datos.paso, 3)
        finally:
            # Limpieza
            if os.path.exists(outliers_path):
                os.remove(outliers_path)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    @patch('matplotlib.pyplot.show')
    def test_opcion3_visualizar_datos(self, mock_plt_show, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de visualización de datos"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "2.3", "2.4", "2.5", "3", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['edad', 'salario'], 'resultado')
        
        # Para realizar todas las operaciones necesarias
        with patch('builtins.input', side_effect=['3', '3', '3', '3', '1']):  # Varias ops y opción de visualización
            datos = Datos()
            
            # Verificamos que se pasó correctamente a la visualización y exportación
            self.assertEqual(datos.paso, 4)
    
    @patch('manejodatos.mostrar_menu')
    @patch('manejodatos.cargar_datos')
    @patch('manejodatos.seleccion_terminal')
    def test_opcion4_exportar_datos(self, mock_seleccion, mock_cargar_datos, mock_menu):
        """Prueba de exportación de datos"""
        # Configuramos los mocks
        mock_menu.side_effect = ["1", "2", "2.1", "2.2", "2.3", "2.4", "2.5", "3", "4", "5"]
        mock_cargar_datos.return_value = (1, self.csv_path)
        mock_seleccion.return_value = (['edad', 'salario'], 'resultado')
        
        # Para realizar todas las operaciones necesarias
        with patch('builtins.input', side_effect=['3', '3', '3', '3', '1', '1', 'test_export']):
            datos = Datos()
            
            # Verificamos que el archivo se exportó correctamente
            self.assertTrue(os.path.exists('test_export.csv'))
            self.assertEqual(datos.paso, 5)

if __name__ == '__main__':
    unittest.main()

