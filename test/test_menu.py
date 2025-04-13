import unittest
from unittest.mock import patch, MagicMock, ANY
import io
import sys
import os

# Añadir la ruta del directorio principal al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd
import menu  # Ahora podrá encontrar el módulo menu

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
        self.parent_dir = os.path.abspath(os.path.join(self.current_dir, '..'))
        self.csv_path = os.path.join(self.parent_dir, "data_test.csv")
        self.excel_path = os.path.join(self.parent_dir, "data_test.xlsx")
        self.sqlite_path = os.path.join(self.parent_dir, "data_test.db")
        
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
        
        # Verificar que se imprimió algo que contiene "Cargar datos" y "ningún archivo cargado"
        found = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str):
                if "1. Cargar datos" in args[0] and "ningún archivo cargado" in args[0]:
                    found = True
                    break
        self.assertTrue(found, "No se encontró la línea del menú para cargar datos")
        
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_mostrar_menu_paso2(self, mock_print, mock_input):
        # Prueba mostrar_menu en paso 2 (datos cargados, preprocesado iniciado)
        result = menu.mostrar_menu(2, self.test_df, "data_test.csv")
        self.assertEqual(result, '5')
        
        # Verificar menú con búsqueda parcial de cadenas
        found_carga = False
        found_preprocesado = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str):
                if "1. Cargar datos" in args[0] and "data_test.csv" in args[0]:
                    found_carga = True
                if "2. Preprocesado de datos" in args[0]:
                    found_preprocesado = True
        
        self.assertTrue(found_carga, "No se encontró la línea del menú para datos cargados")
        self.assertTrue(found_preprocesado, "No se encontró la línea del menú para preprocesado")
        
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')
    def test_mostrar_menu_paso3(self, mock_print, mock_input):
        # Prueba mostrar_menu en paso 3 (preprocesado completo)
        result = menu.mostrar_menu(3, self.test_df, "data_test.csv")
        self.assertEqual(result, '5')
        
        # Verificar submenús con búsqueda parcial
        found_seleccion = False
        found_valores_faltantes = False
        found_visualizacion = False
        
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str):
                if "2.1 Selección de columnas" in args[0]:
                    found_seleccion = True
                if "2.2 Manejo de valores faltantes" in args[0]:
                    found_valores_faltantes = True
                if "3. Visualización de datos" in args[0]:
                    found_visualizacion = True
        
        self.assertTrue(found_seleccion, "No se encontró la línea de selección de columnas")
        self.assertTrue(found_valores_faltantes, "No se encontró la línea de manejo de valores faltantes")
        self.assertTrue(found_visualizacion, "No se encontró la línea de visualización de datos")
        
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
        # Buscar mensaje de error en las llamadas a print
        found = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str) and "Opción inválida" in args[0]:
                found = True
                break
        self.assertTrue(found, "No se mostró el mensaje de opción inválida")
        
    @patch('builtins.print')
    def test_mostrar_datos(self, mock_print):
        # Prueba mostrar_datos
        menu.mostrar_datos(self.test_df, "data_test.csv")
        
        # Buscar mensajes en las llamadas a print
        found_cargados = False
        found_fuente = False
        found_filas = False
        found_columnas = False
        
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str):
                if "Datos cargados correctamente" in args[0]:
                    found_cargados = True
                elif "Fuente:" in args[0]:
                    found_fuente = True
                elif "Número de filas:" in args[0]:
                    found_filas = True
                elif "Número de columnas:" in args[0]:
                    found_columnas = True
        
        self.assertTrue(found_cargados, "No se mostró el mensaje de datos cargados")
        self.assertTrue(found_fuente, "No se mostró la fuente de los datos")
        self.assertTrue(found_filas, "No se mostró el número de filas")
        self.assertTrue(found_columnas, "No se mostró el número de columnas")
        
    @patch('builtins.input', side_effect=['1,2', '3'])
    @patch('builtins.print')
    def test_seleccion_terminal(self, mock_print, mock_input):
        # Prueba seleccion_terminal
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')

    @patch('builtins.input', side_effect=['1,5', '1,2', '3'])  # Primero opción fuera de rango, luego válida
    @patch('builtins.print')
    def test_seleccion_terminal_opcion_invalida(self, mock_print, mock_input):
        # Prueba seleccion_terminal con una selección inválida primero
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')
        
        # Buscar mensaje de error en las llamadas a print
        found = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str) and "fuera del rango" in args[0]:
                found = True
                break
        self.assertTrue(found, "No se mostró el mensaje de opción fuera de rango")
        
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
            
            # Buscar mensaje en las llamadas a print
            found = False
            for call in mock_print.call_args_list:
                args, _ = call
                if len(args) > 0 and isinstance(args[0], str) and "Regresando al menú principal" in args[0]:
                    found = True
                    break
            self.assertTrue(found, "No se mostró el mensaje de regreso al menú principal")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa cuando se elige 'No'")
            
    @patch('builtins.input', side_effect=['3', '2'])  # Primero opción inválida, luego "No"
    @patch('builtins.print')
    def test_cerrar_opcion_invalida(self, mock_print, mock_input):
        # Prueba cerrar con una opción inválida
        try:
            menu.cerrar()
            # Debería llegar aquí si el programa no termina
            
            # Buscar mensaje de error en las llamadas a print
            found = False
            for call in mock_print.call_args_list:
                args, _ = call
                if len(args) > 0 and isinstance(args[0], str) and "Opción inválida" in args[0]:
                    found = True
                    break
            self.assertTrue(found, "No se mostró el mensaje de opción inválida")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa con una opción inválida")
            
    @patch('builtins.input', return_value='1')  # Seleccionar "Sí" para salir
    def test_cerrar_salir(self, mock_input):
        # Prueba cerrar cuando el usuario elige salir
        with self.assertRaises(SystemExit) as cm:
            menu.cerrar()
        self.assertEqual(cm.exception.code, 0)  # Verifica que el código de salida sea 0

    @patch('menu.obtener_indice_valido', side_effect=[0, 2])  # Primer intento es col1, segundo es col3
    @patch('builtins.input', side_effect=['1,2', '1'])  # Primero features, luego target (igual que una feature)
    @patch('builtins.print')
    def test_seleccion_terminal_target_en_features(self, mock_print, mock_input, mock_get_index):
        # Prueba cuando el usuario intenta seleccionar un target que ya es feature
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')
        
        # Buscar mensaje de error en las llamadas a print
        found = False
        for call in mock_print.call_args_list:
            args, _ = call
            if len(args) > 0 and isinstance(args[0], str) and "ya está seleccionada como feature" in args[0]:
                found = True
                break
        self.assertTrue(found, "No se mostró el mensaje de target ya seleccionado como feature")

if __name__ == '__main__':
    unittest.main()
