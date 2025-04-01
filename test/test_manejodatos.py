
import unittest
from unittest.mock import patch, MagicMock
import os
import pandas as pd
from manejodatos import Datos

class TestDatos(unittest.TestCase):

    @patch('manejodatos.pd.read_csv')  # Mockea la función pd.read_csv
    def test_cargar_datos_csv(self, mock_read_csv):
        # Simulamos que pd.read_csv devuelve un DataFrame cuando se llama
        mock_read_csv.return_value = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        
        # Creamos un objeto de la clase Datos
        datos = Datos()
        ruta = 'ruta/al/archivo.csv'
        
        # Simulamos la carga de datos
        datos.opcion1_carga()
        
        # Comprobamos que los datos se cargaron correctamente
        self.assertIsNotNone(datos.datos)
        self.assertEqual(datos.datos.shape, (3, 2))  # Comprobamos que el DataFrame tiene 3 filas y 2 columnas

    @patch('builtins.input', return_value='1')  # Mockea la entrada para que siempre devuelva '1'
    @patch('manejodatos.mostrar_menu', return_value='1')  # Mockea el menú para simular que se elige la opción 1
    def test_proceso_cargar_datos(self, mock_menu, mock_input):
        # Simulamos que no hay datos cargados y se elige cargar datos
        datos = Datos(file_path=None)
        
        # Aseguramos que la opción cargue los datos correctamente
        self.assertEqual(datos.paso, 2)  # El paso debe ser 2 después de cargar los datos
    
    @patch('builtins.input', return_value='1')
    def test_opcion2_selector_columnas(self, mock_input):
        # Simula la selección de columnas
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': [1, 2], 'col2': [3, 4], 'col3': [5, 6]})
        datos.features = ['col1', 'col2', 'col3']
        
        # Simula la selección de columnas
        datos.opcion2_selector_columnas()
        
        self.assertEqual(datos.features, ['col1', 'col2', 'col3'])
        self.assertEqual(datos.targets, 'col1')  # Suponiendo que el usuario selecciona 'col1' como la columna objetivo

    @patch('builtins.input', return_value='2')
    def test_opcion2_manejo_nulos(self, mock_input):
        # Simula la detección y manejo de valores nulos
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': [1, None], 'col2': [None, 4]})
        datos.features = ['col1', 'col2']
        datos.targets = 'col1'

        # Ejecutamos el método de manejo de nulos
        datos.opcion2_manejo_nulos()

        # Comprobamos que los nulos se manejaron
        self.assertFalse(datos.datos['col1'].isnull().any())  # No debe haber valores nulos
        self.assertFalse(datos.datos['col2'].isnull().any())  # No debe haber valores nulos

    @patch('builtins.input', return_value='1')
    def test_opcion2_transformar_categoricos(self, mock_input):
        # Simula la transformación de datos categóricos
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': ['a', 'b', 'a'], 'col2': [1, 2, 3]})
        datos.features = ['col1']
        
        # Simula la transformación de datos categóricos
        datos.opcion2_transformar_categoricos()
        
        # Comprobamos que la columna 'col1' se ha transformado correctamente
        self.assertTrue((datos.datos['col1'] == [0, 1, 0]).all())  # Se aplica Label Encoding

    @patch('builtins.input', return_value='1')
    def test_opcion2_normalizar_numericas(self, mock_input):
        # Simula la normalización de datos numéricos
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        datos.features = ['col1', 'col2']
        
        # Realizamos la normalización
        datos.opcion2_normalizar_numericas()
        
        # Comprobamos que las columnas fueron normalizadas (valores entre 0 y 1)
        self.assertTrue(datos.datos['col1'].max() <= 1)
        self.assertTrue(datos.datos['col2'].max() <= 1)

    @patch('builtins.input', return_value='1')
    def test_opcion2_manejo_atipicos(self, mock_input):
        # Simula el manejo de valores atípicos
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': [1, 2, 1000], 'col2': [4, 5, 6]})
        datos.features = ['col1', 'col2']
        
        # Ejecutamos el manejo de valores atípicos
        datos.opcion2_manejo_atipicos()
        
        # Verificamos que los valores atípicos fueron tratados
        self.assertNotIn(1000, datos.datos['col1'])  # El valor atípico debe haberse eliminado

    def test_opcion3_visualizar_datos(self):
        # Simula la visualización de datos
        datos = Datos(file_path=None)
        datos.datos = pd.DataFrame({'col1': [1, 2, 3], 'col2': [4, 5, 6]})
        datos.features = ['col1', 'col2']
        
        # Realizamos una visualización
        datos.opcion3_visualizar_datos()
        
        # Verifica que se generó una visualización correctamente
        # Esto depende de la implementación de visualización, pero si usas plt.show() deberías comprobar que no haya errores

if __name__ == '__main__':
    unittest.main()

