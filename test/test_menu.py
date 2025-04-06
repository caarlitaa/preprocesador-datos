import unittest
from unittest.mock import patch, MagicMock
import pandas as pd
import os
import sys
import io
from contextlib import contextmanager

# Importar el módulo menu
import menu

class TestMenu(unittest.TestCase):
    
    def setUp(self):
        # Configuración común para las pruebas
        self.columnas_ejemplo = ['PassengerId', 'Survived', 'Pclass', 'Name', 'Sex', 'Age', 'SibSp', 'Parch', 'Ticket', 'Fare', 'Cabin', 'Embarked']
        
        # Ruta a los archivos de datos reales para pruebas
        self.csv_path = 'titanic_survival.csv'  
        self.excel_path = 'titanic_survival.xlsx'  
        self.sqlite_path = 'titanic_survival.db'  
        
        # Verifica que los archivos existan para las pruebas
        self.files_exist = (
            os.path.exists(self.csv_path) and 
            os.path.exists(self.excel_path) and 
            os.path.exists(self.sqlite_path)
        )
    
    def test_simbolo(self):
        # Probar la función símbolo con diferentes casos
        self.assertEqual(menu.simbolo(1, 0), '✗')  # Paso no alcanzado
        self.assertEqual(menu.simbolo(2, 2), '-')  # Paso en ejecución
        self.assertEqual(menu.simbolo(2, 2.5), '-')  # Caso especial para paso 2
        self.assertEqual(menu.simbolo(1, 2), '✓')  # Paso completado
    
    @patch('builtins.print')
    @patch('builtins.input', return_value='1')
    def test_mostrar_menu_datos_no_cargados(self, mock_input, mock_print):
        # Probar mostrar_menu cuando los datos no están cargados
        paso = 1
        datos = None
        ruta = None
        
        resultado = menu.mostrar_menu(paso, datos, ruta)
        
        # Verificar que la función devuelve la opción correcta
        self.assertEqual(resultado, '1')
        
        # Verificar que print fue llamado con argumentos específicos
        mock_print.assert_any_call("[✗] 1. Cargar datos (ningún archivo cargado)")
    
    @patch('builtins.print')
    @patch('builtins.input', return_value='2')
    def test_mostrar_menu_datos_cargados(self, mock_input, mock_print):
        # Probar mostrar_menu cuando los datos están cargados
        paso = 2
        datos = pd.DataFrame({col: [1, 2, 3] for col in self.columnas_ejemplo})
        ruta = self.csv_path if self.files_exist else 'titanic.csv'
        
        resultado = menu.mostrar_menu(paso, datos, ruta)
        
        # Verificar que la función devuelve la opción correcta
        self.assertEqual(resultado, '2')
        
        # Verificar que print fue llamado con los argumentos esperados
        mock_print.assert_any_call(f"[{menu.simbolo(1, paso)}] 1. Cargar datos (archivo {ruta} cargado)")
    
    @patch('builtins.print')
    @patch('os.path.exists', return_value=True)
    def test_cargar_datos_csv(self, mock_exists, mock_print):
        # Probar cargar_datos con un archivo CSV
        with patch('builtins.input', side_effect=['1', self.csv_path if self.files_exist else 'titanic.csv']):
            resultado = menu.cargar_datos()
            
            # Verificar que devuelve la opción y la ruta correctas
            self.assertEqual(resultado[0], 1)  # Opción CSV
            self.assertTrue(resultado[1].endswith('.csv'))  # Ruta termina en .csv
    
    @patch('builtins.print')
    def test_cargar_datos_volver(self, mock_print):
        # Probar cargar_datos cuando se selecciona volver
        with patch('builtins.input', return_value='4'):
            resultado = menu.cargar_datos()
            
            # Verificar que devuelve None
            self.assertIsNone(resultado)
    
    @patch('builtins.print')
    def test_mostrar_datos(self, mock_print):
        # Probar mostrar_datos
        # Si los archivos existen, cargar datos reales
        if self.files_exist and os.path.exists(self.csv_path):
            datos = pd.read_csv(self.csv_path)
        else:
            datos = pd.DataFrame({col: [1, 2, 3] for col in self.columnas_ejemplo})
        
        fuente = self.csv_path if self.files_exist else 'titanic.csv'
        
        menu.mostrar_datos(datos, fuente)
        
        # Verificar que print fue llamado con los argumentos esperados
        mock_print.assert_any_call("\nDatos cargados correctamente.")
        mock_print.assert_any_call(f"Fuente: {fuente}")
        mock_print.assert_any_call(f"Número de filas: {datos.shape[0]}")
        mock_print.assert_any_call(f"Número de columnas: {datos.shape[1]}")
    
    @patch('builtins.print')
    @patch('menu.obtener_indice_valido', return_value=1)  # Simulará la selección de 'Survived' como target
    def test_seleccion_terminal(self, mock_indice, mock_print):
        # Probar seleccion_terminal
        with patch('builtins.input', return_value='1,3,5'):  # Simulará la selección de columnas
            columnas = self.columnas_ejemplo
            
            features, target = menu.seleccion_terminal(columnas)
            
            # Verificar que devuelve las features y target correctos
            self.assertEqual(features, ['PassengerId', 'Name', 'Age'])
            self.assertEqual(target, 'Survived')
    
    @patch('builtins.print')
    def test_obtener_indice_valido(self, mock_print):
        # Probar obtener_indice_valido
        with patch('builtins.input', side_effect=['5', '1']):  # Entrada inválida, luego válida
            resultado = menu.obtener_indice_valido("Mensaje de prueba:", 4)
            
            # Verificar que devuelve el índice correcto (base 0)
            self.assertEqual(resultado, 0)
    
    @patch('builtins.print')
    @patch('sys.exit')
    def test_cerrar_si(self, mock_exit, mock_print):
        # Probar cerrar cuando se selecciona 'Sí'
        with self.assertRaises(SystemExit):
            menu.cerrar()
            
            # Verificar que sys.exit fue llamado con 0
            mock_exit.assert_called_once_with(0)
    
    @patch('builtins.print')
    def test_cerrar_no(self, mock_print):
        # Probar cerrar cuando se selecciona 'No'
        with patch('builtins.input', return_value='2'):
            menu.cerrar()
            
            # Verificar que print fue llamado con los argumentos esperados
            mock_print.assert_any_call("\nRegresando al menú principal...")
    
    # Añadimos un método tearDown para limpiar después de las pruebas
    def tearDown(self):
        # Limpiar recursos si es necesario
        pass

if __name__ == '__main__':
    unittest.main()