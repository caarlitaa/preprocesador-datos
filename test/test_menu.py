import pytest
from unittest.mock import patch
import pandas as pd
import menu  # Asegúrate de que el nombre del archivo sea correcto

def test_simbolo_paso_no_alcanzado():
    """Prueba que el símbolo sea '✗' cuando el paso no ha sido alcanzado."""
    assert menu.simbolo(2, 1) == '✗'

def test_simbolo_paso_en_ejecucion():
    """Prueba que el símbolo sea '-' cuando el paso está en ejecución."""
    assert menu.simbolo(2, 2) == '-'
    assert menu.simbolo(2, 2.5) == '-'

def test_simbolo_paso_completado():
    """Prueba que el símbolo sea '✓' cuando el paso ha sido completado."""
    assert menu.simbolo(2, 3) == '✓'

def test_mostrar_menu_opcion_valida():
    """Prueba que mostrar_menu devuelva la opción seleccionada."""
    with patch('builtins.input', return_value='1'):
        assert menu.mostrar_menu(1, None, None) == '1'

def test_cargar_datos_opcion_valida():
    """Prueba que cargar_datos devuelva la opción y la ruta."""
    with patch('builtins.input', side_effect=['1', 'test.csv']):
        assert menu.cargar_datos() == (1, 'test.csv')

def test_cargar_datos_opcion_volver_menu():
    """Prueba que cargar_datos devuelva None cuando la opción es 4."""
    with patch('builtins.input', return_value='4'):
        assert menu.cargar_datos() is None

def test_mostrar_datos():
    """Prueba que mostrar_datos imprima la información correcta."""
    datos = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
    with patch('builtins.print') as mock_print:
        menu.mostrar_datos(datos, 'test.csv')
        mock_print.assert_called()  # Verifica que se llamó a print

def test_seleccion_terminal_opcion_valida():
    """Prueba que seleccion_terminal devuelva las columnas seleccionadas."""
    columnas = ['A', 'B', 'C']
    with patch('builtins.input', side_effect=['1, 2', '3']):
        assert menu.seleccion_terminal(columnas) == (['A', 'B'], 'C')

def test_obtener_indice_valido_opcion_valida():
    """Prueba que obtener_indice_valido devuelva el índice correcto."""
    with patch('builtins.input', return_value='2'):
        assert menu.obtener_indice_valido('mensaje', 3) == 1

def test_cerrar_opcion_salir():
    """Prueba que cerrar termine el programa cuando la opción es 1."""
    with patch('builtins.input', return_value='1'):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            menu.cerrar()
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == 0

def test_cerrar_opcion_volver_menu():
    """Prueba que cerrar vuelva al menú principal cuando la opción es 2."""
    with patch('builtins.input', return_value='2'):
        menu.cerrar()  # No debería haber errores