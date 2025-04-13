import unittest
from unittest.mock import patch, MagicMock
import io
import sys
import os
import pandas as pd
import menu  # Importamos el módulo menu.py

class TestMenuFunctions(unittest.TestCase):
    
    def setUp(self):
        # Crear un DataFrame de prueba
        self.test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [True, False, True]
        })
        
        # Configurar rutas de archivos de prueba
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(self.current_dir, "data_test.csv")
        self.excel_path = os.path.join(self.current_dir, "data_test.xlsx")
        self.sqlite_path = os.path.join(self.current_dir, "data_test.db")
        
        # Crear archivos de prueba si no existen
        if not os.path.exists(self.csv_path):
            self.test_df.to_csv(self.csv_path, index=False)
        if not os.path.exists(self.excel_path):
            self.test_df.to_excel(self.excel_path, index=False)
        # No creamos el archivo SQLite para las pruebas para simplificar
        
    def tearDown(self):
        # Limpiar archivos de prueba
        for file_path in [self.csv_path, self.excel_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    
    def test_simbolo(self):
        # Prueba cuando el paso no se ha alcanzado
        self.assertEqual(menu.simbolo(3, 1), '✗')
        # Prueba cuando el paso está en ejecución (caso normal)
        self.assertEqual(menu.simbolo(2, 2), '-')
        # Prueba del caso especial para paso 2
        self.assertEqual(menu.simbolo(2, 2.5), '-')
        # Prueba cuando el paso se ha completado
        self.assertEqual(menu.simbolo(1, 2), '✓')
        
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_mostrar_menu_paso1(self, mock_print, mock_input):
        # Prueba mostrar_menu en paso 1 (sin datos cargados)
        result = menu.mostrar_menu(1, None, "")
        self.assertEqual(result, '5')
        # Verificar que se imprimió el menú con los símbolos correctos
        mock_print.assert_any_call("[✗] 1. Cargar datos (ningún archivo cargado)")
        
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_mostrar_menu_paso2(self, mock_print, mock_input):
        # Prueba mostrar_menu en paso 2 (datos cargados, preprocesado iniciado)
        result = menu.mostrar_menu(2, self.test_df, "data_test.csv")
        self.assertEqual(result, '5')
        # Verificar que se imprimió el menú con los símbolos correctos
        mock_print.assert_any_call("[✓] 1. Cargar datos (archivo data_test.csv cargado)")
        mock_print.assert_any_call("[−] 2. Preprocesado de datos (selección de columnas requerida)")
        
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_mostrar_menu_paso3(self, mock_print, mock_input):
        # Prueba mostrar_menu en paso 3 (preprocesado completo)
        result = menu.mostrar_menu(3, self.test_df, "data_test.csv")
        self.assertEqual(result, '5')
        # Verificar que se imprimieron los submenús de preprocesado
        mock_print.assert_any_call("\t[✓] 2.1 Selección de columnas (completado)")
        mock_print.assert_any_call("\t[✓] 2.2 Manejo de valores faltantes (completado)")
        mock_print.assert_any_call("[−] 3. Visualización de datos (pendiente)")
        
    @patch('builtins.input', side_effect=['1', 'data_test.csv'])
    def test_cargar_datos_csv(self, mock_input):
        # Prueba cargar_datos seleccionando un archivo CSV en la misma carpeta
        result = menu.cargar_datos()
        self.assertEqual(result, (1, 'data_test.csv'))
        
    @patch('builtins.input', side_effect=['2', 'data_test.xlsx'])
    def test_cargar_datos_excel(self, mock_input):
        # Prueba cargar_datos seleccionando un archivo Excel en la misma carpeta
        result = menu.cargar_datos()
        self.assertEqual(result, (2, 'data_test.xlsx'))
        
    @patch('builtins.input', side_effect=['3', 'data_test.db'])
    def test_cargar_datos_sqlite(self, mock_input):
        # Prueba cargar_datos seleccionando un archivo SQLite en la misma carpeta
        result = menu.cargar_datos()
        self.assertEqual(result, (3, 'data_test.db'))
        
    @patch('builtins.input', side_effect=['4'])
    def test_cargar_datos_volver(self, mock_input):
        # Prueba cargar_datos seleccionando volver al menú principal
        result = menu.cargar_datos()
        self.assertEqual(result, None)
        
    @patch('builtins.input', side_effect=['6', '4'])  # Opción inválida, luego volver
    @patch('builtins.print')
    def test_cargar_datos_opcion_invalida(self, mock_print, mock_input):
        # Prueba cargar_datos con una opción inválida
        result = menu.cargar_datos()
        self.assertEqual(result, None)
        mock_print.assert_any_call("Opción inválida. Intente de nuevo.")
        
    @patch('builtins.print')
    def test_mostrar_datos(self, mock_print):
        # Prueba mostrar_datos
        menu.mostrar_datos(self.test_df, "data_test.csv")
        mock_print.assert_any_call("\nDatos cargados correctamente.")
        mock_print.assert_any_call("Fuente: data_test.csv")
        mock_print.assert_any_call(f"Número de filas: {self.test_df.shape[0]}")
        mock_print.assert_any_call(f"Número de columnas: {self.test_df.shape[1]}")
        
    @patch('builtins.input', side_effect=['1,2', '3'])
    @patch('builtins.print')
    def test_seleccion_terminal(self, mock_print, mock_input):
        # Prueba seleccion_terminal
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col4')

    @patch('builtins.input', side_effect=['1,5', '1,2', '3'])  # Primero opción fuera de rango, luego válida
    @patch('builtins.print')
    def test_seleccion_terminal_opcion_invalida(self, mock_print, mock_input):
        # Prueba seleccion_terminal con una selección inválida primero
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col4')
        mock_print.assert_any_call("\nError: La columna '5' está fuera del rango. Debe seleccionar un número entre 1 y 4.")
        
    @patch('builtins.input', side_effect=['10', '2'])  # Primero una opción fuera de rango, luego válida
    def test_obtener_indice_valido(self, mock_input):
        # Prueba obtener_indice_valido
        result = menu.obtener_indice_valido("Mensaje:", 5)
        self.assertEqual(result, 1)  # Debería devolver 1 (índice base 0 de la opción 2)
        
    @patch('builtins.input', side_effect=['2'])  # Seleccionar "No" para no salir
    @patch('builtins.print')
    def test_cerrar_no_salir(self, mock_print, mock_input):
        # Prueba cerrar cuando el usuario elige no salir
        try:
            menu.cerrar()
            # Debería llegar aquí si el programa no termina
            mock_print.assert_any_call("\nRegresando al menú principal...")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa cuando se elige 'No'")
            
    @patch('builtins.input', side_effect=['3', '2'])  # Primero opción inválida, luego "No"
    @patch('builtins.print')
    def test_cerrar_opcion_invalida(self, mock_print, mock_input):
        # Prueba cerrar con una opción inválida
        try:
            menu.cerrar()
            # Debería llegar aquí si el programa no termina
            mock_print.assert_any_call("\nOpción inválida. Intente de nuevo.")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa con una opción inválida")
            
    @patch('builtins.input', return_value='1')  # Seleccionar "Sí" para salir
    def test_cerrar_salir(self, mock_input):
        # Prueba cerrar cuando el usuario elige salir
        with self.assertRaises(SystemExit) as cm:
            menu.cerrar()
        self.assertEqual(cm.exception.code, 0)  # Verifica que el código de salida sea 0

    @patch('builtins.input', side_effect=['1,2', '1'])  # Primero features, luego target (igual que una feature)
    @patch('builtins.print')
    def test_seleccion_terminal_target_en_features(self, mock_print, mock_input):
        # Prueba cuando el usuario intenta seleccionar un target que ya es feature
        columnas = ['col1', 'col2', 'col3', 'col4']
        with patch('menu.obtener_indice_valido', side_effect=[0, 2]):  # Primer intento es col1, segundo es col3
            features, target = menu.seleccion_terminal(columnas)
            self.assertEqual(features, ['col1', 'col2'])
            self.assertEqual(target, 'col3')
            mock_print.assert_any_call("\nError: La columna 'col1' ya está seleccionada como feature. Debe seleccionar un target que no esté en features")

if __name__ == '__main__':
    unittest.main()
