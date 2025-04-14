
import unittest
from unittest.mock import patch, MagicMock, ANY
import io
import sys
import os
import pandas as pd

# Añadir la ruta del directorio principal al sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import menu  

class TestMenuFunciones(unittest.TestCase):
    
    # Crear un DataFrame de prueba
    def setUp(self):
        self.test_df = pd.DataFrame({
            'col1': [1, 2, 3],
            'col2': ['a', 'b', 'c'],
            'col3': [True, False, True]
        })
        
        # Configurar rutas de archivos de prueba
        self.current_dir = os.path.dirname(os.path.abspath(__file__))
        self.parent_dir = os.path.abspath(os.path.join(self.current_dir, '..'))
        self.csv_path = os.path.join(self.parent_dir, "test.csv")
        self.excel_path = os.path.join(self.parent_dir, "test.xlsx")
        self.sqlite_path = os.path.join(self.parent_dir, "test.db")
        
        # Crear archivos de prueba si no existen
        if not os.path.exists(self.csv_path):
            self.test_df.to_csv(self.csv_path, index=False)
        if not os.path.exists(self.excel_path):
            self.test_df.to_excel(self.excel_path, index=False)

    # Limpiar archivos de prueba    
    def tearDown(self):
        for file_path in [self.csv_path, self.excel_path]:
            if os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass
    
    # Prueba los diferentes estados del paso
    def test_simbolo(self):
        self.assertEqual(menu.simbolo(3, 1), '✗') # No alcanzado
        
        self.assertEqual(menu.simbolo(2, 2), '-') # En ejecución
        self.assertEqual(menu.simbolo(2, 2.5), '-')
        
        self.assertEqual(menu.simbolo(1, 2), '✓') # Completado
        
    # Mostrar menú sin datos cargados
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')

    def test_mostrar_menu_paso1(self, mock_print, mock_input): 
        resultado = menu.mostrar_menu(1, None, "")
        self.assertEqual(resultado, '5')
        
        # Verificar que se imprimió algo que contiene "Cargar datos" y "ningún archivo cargado"
        linea = False
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str):
                if "1. Cargar datos" in args[0] and "ningún archivo cargado" in args[0]:
                    linea = True
                    break
        self.assertTrue(linea, "No se encontró la línea del menú para cargar datos")

    # Mostrar menú con datos cargados   
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')

    def test_mostrar_menu_paso2(self, mock_print, mock_input):
        resultado = menu.mostrar_menu(2, self.test_df, "test.csv")
        self.assertEqual(resultado, '5')
        
        # Verificar menú con búsqueda parcial de cadenas
        carga = False
        preprocesado = False
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str):
                if "1. Cargar datos" in args[0] and "test.csv" in args[0]:
                    carga = True
                if "2. Preprocesado de datos" in args[0]:
                    preprocesado = True
        
        self.assertTrue(carga, "No se encontró la línea del menú para datos cargados")
        self.assertTrue(preprocesado, "No se encontró la línea del menú para preprocesado")

    #Mostrar menú cuando se completa el preprocesado   
    @patch('builtins.input', return_value='5')
    @patch('builtins.print')

    def test_mostrar_menu_paso3(self, mock_print, mock_input):
        resultado = menu.mostrar_menu(3, self.test_df, "test.csv")
        self.assertEqual(resultado, '5')
        
        # Verificar submenús con búsqueda parcial
        seleccion = False
        valores_faltantes = False
        visualizacion = False
        
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str):
                if "2.1 Selección de columnas" in args[0]:
                    seleccion = True
                if "2.2 Manejo de valores faltantes" in args[0]:
                    valores_faltantes = True
                if "3. Visualización de datos" in args[0]:
                    visualizacion = True
        
        self.assertTrue(seleccion, "No se encontró la línea de selección de columnas")
        self.assertTrue(valores_faltantes, "No se encontró la línea de manejo de valores faltantes")
        self.assertTrue(visualizacion, "No se encontró la línea de visualización de datos")

    # Prueba cargar_datos seleccionando un archivo CSV    
    @patch('builtins.input', side_effect=['1', 'test.csv'])

    def test_cargar_datos_csv(self, mock_input):
        resultado = menu.cargar_datos()
        self.assertEqual(resultado, (1, 'test.csv'))

    # Prueba cargar_datos seleccionando un archivo Excel   
    @patch('builtins.input', side_effect=['2', 'test.xlsx'])

    def test_cargar_datos_excel(self, mock_input):
        resultado = menu.cargar_datos()
        self.assertEqual(resultado, (2, 'test.xlsx'))

    # Prueba cargar_datos seleccionando un archivo SQLite   
    @patch('builtins.input', side_effect=['3', 'test.db'])

    def test_cargar_datos_sqlite(self, mock_input):
        resultado = menu.cargar_datos()
        self.assertEqual(resultado, (3, 'test.db'))

    # Prueba cargar_datos seleccionando volver al menú principal    
    @patch('builtins.input', side_effect=['4'])

    def test_cargar_datos_volver(self, mock_input):
        resultado = menu.cargar_datos()
        self.assertEqual(resultado, None)

    # Prueba cargar_datos con una opción inválida    
    @patch('builtins.input', side_effect=['6', '4'])  # Opción inválida, luego volver
    @patch('builtins.print')

    def test_cargar_datos_opcion_invalida(self, mock_print, mock_input):
        resultado = menu.cargar_datos()
        self.assertEqual(resultado, None)

        # Buscar mensaje de error en las llamadas a print
        mensaje = False
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str) and "Opción inválida" in args[0]:
                mensaje = True
                break
        self.assertTrue(mensaje, "No se mostró el mensaje de opción inválida")

     # Prueba mostrar_datos   
    @patch('builtins.print')

    def test_mostrar_datos(self, mock_print):
        menu.mostrar_datos(self.test_df, "test.csv")
        
        # Buscar mensajes en las llamadas a print
        cargados = False
        fuente = False
        filas = False
        columnas = False
        
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str):
                if "Datos cargados correctamente" in args[0]:
                    cargados = True
                elif "Fuente:" in args[0]:
                    fuente = True
                elif "Número de filas:" in args[0]:
                    filas = True
                elif "Número de columnas:" in args[0]:
                    columnas = True
        
        self.assertTrue(cargados, "No se mostró el mensaje de datos cargados")
        self.assertTrue(fuente, "No se mostró la fuente de los datos")
        self.assertTrue(filas, "No se mostró el número de filas")
        self.assertTrue(columnas, "No se mostró el número de columnas")

    # Prueba seleccion_terminal   
    @patch('builtins.input', side_effect=['1,2', '3'])
    @patch('builtins.print')

    def test_seleccion_terminal(self, mock_print, mock_input):
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')

    # Prueba seleccion_terminal con una selección inválida 
    @patch('builtins.input', side_effect=['1,5', '1,2', '3'])  
    @patch('builtins.print')

    def test_seleccion_terminal_opcion_invalida(self, mock_print, mock_input):
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')
        
        # Buscar mensaje de error en las llamadas a print
        mensaje = False
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str) and "fuera del rango" in args[0]:
                mensaje = True
                break
        self.assertTrue(mensaje, "No se mostró el mensaje de opción fuera de rango")

    # Prueba obtener_indice_valido   
    @patch('builtins.input', side_effect=['10', '2']) 

    def test_obtener_indice_valido(self, mock_input):
        resultado = menu.obtener_indice_valido("Mensaje:", 5)
        self.assertEqual(resultado, 1) 

    # Prueba cerrar cuando el usuario elige no salir    
    @patch('builtins.input', side_effect=['2'])  
    @patch('builtins.print')

    def test_cerrar_no_salir(self, mock_print, mock_input):
        try:
            menu.cerrar()
            
            # Buscar mensaje en las llamadas a print
            mensaje = False
            for llamada in mock_print.call_args_list:
                args, _ = llamada
                if len(args) > 0 and isinstance(args[0], str) and "Regresando al menú principal" in args[0]:
                    mensaje = True
                    break
            self.assertTrue(mensaje, "No se mostró el mensaje de regreso al menú principal")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa cuando se elige 'No'")

     # Prueba cerrar con una opción inválida        
    @patch('builtins.input', side_effect=['3', '2'])  
    @patch('builtins.print')

    def test_cerrar_opcion_invalida(self, mock_print, mock_input):
        try:
            menu.cerrar()
            
            # Buscar mensaje de error en las llamadas a print
            mensaje = False
            for llamada in mock_print.call_args_list:
                args, _ = llamada
                if len(args) > 0 and isinstance(args[0], str) and "Opción inválida" in args[0]:
                    mensaje = True
                    break
            self.assertTrue(mensaje, "No se mostró el mensaje de opción inválida")
        except SystemExit:
            self.fail("cerrar() no debería terminar el programa con una opción inválida")

    # Prueba cerrar cuando el usuario elige salir        
    @patch('builtins.input', return_value='1') 

    def test_cerrar_salir(self, mock_input):
        with self.assertRaises(SystemExit) as cm:
            menu.cerrar()
        self.assertEqual(cm.exception.code, 0)  # Verifica que el código de salida sea 0

    # Prueba cuando el usuario intenta seleccionar un target que ya es feature
    @patch('menu.obtener_indice_valido', side_effect=[0, 2])  
    @patch('builtins.input', side_effect=['1,2', '1']) 
    @patch('builtins.print')

    def test_seleccion_terminal_target_en_features(self, mock_print, mock_input, mock_get_index):
        columnas = ['col1', 'col2', 'col3', 'col4']
        features, target = menu.seleccion_terminal(columnas)
        self.assertEqual(features, ['col1', 'col2'])
        self.assertEqual(target, 'col3')
        
        # Buscar mensaje de error en las llamadas a print
        mensaje = False
        for llamada in mock_print.call_args_list:
            args, _ = llamada
            if len(args) > 0 and isinstance(args[0], str) and "ya está seleccionada como feature" in args[0]:
                mensaje = True
                break
        self.assertTrue(mensaje, "No se mostró el mensaje de target ya seleccionado como feature")

if __name__ == '__main__':
    unittest.main()