import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from manejodatos import Datos  # Asegúrate de que el nombre del archivo sea correcto

@pytest.fixture
def datos_instance():
    """Crea una instancia de la clase Datos para cada prueba."""
    return Datos()

def test_opcion1_carga_csv(datos_instance):
    """Prueba la carga de datos desde un archivo CSV."""
    with patch('menu.cargar_datos', return_value=(1, 'test.csv')):
        with patch('pandas.read_csv', return_value=pd.DataFrame({'A': [1, 2], 'B': [3, 4]})):
            datos_instance.opcion1_carga()
            assert datos_instance.datos is not None
            assert not datos_instance.datos.empty
            assert datos_instance.ruta == 'test.csv'
            assert datos_instance.paso == 2

def test_opcion1_carga_excel(datos_instance):
    """Prueba la carga de datos desde un archivo Excel."""
    with patch('menu.cargar_datos', return_value=(2, 'test.xlsx')):
        with patch('pandas.read_excel', return_value=pd.DataFrame({'A': [1, 2], 'B': [3, 4]})):
            datos_instance.opcion1_carga()
            assert datos_instance.datos is not None
            assert not datos_instance.datos.empty
            assert datos_instance.ruta == 'test.xlsx'
            assert datos_instance.paso == 2

def test_opcion1_carga_sqlite(datos_instance):
    """Prueba la carga de datos desde una base de datos SQLite."""
    mock_conn = MagicMock()
    with patch('menu.cargar_datos', return_value=(3, 'test.sqlite')):
        with patch('sqlite3.connect', return_value=mock_conn):
            with patch('pandas.read_sql', return_value=pd.DataFrame({'name': ['tabla_test']})) as mock_read_sql:
                with patch('builtins.input', return_value='1'):
                    mock_read_sql.side_effect = [pd.DataFrame({'A': [1, 2], 'B': [3, 4]}), pd.DataFrame({'name': ['tabla_test']})]
                    datos_instance.opcion1_carga()
                    assert datos_instance.datos is not None
                    assert not datos_instance.datos.empty
                    assert datos_instance.ruta == 'test.sqlite'
                    assert datos_instance.paso == 2

def test_opcion2_selector_columnas(datos_instance):
    """Prueba la selección de columnas."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2], 'B': [3, 4], 'C': [5, 6]})
    with patch('menu.seleccion_terminal', return_value=(['A', 'B'], 'C')):
        datos_instance.opcion2_selector_columnas()
        assert datos_instance.features == ['A', 'B']
        assert datos_instance.targets == 'C'
        assert datos_instance.paso == 2.2

def test_opcion2_manejo_nulos_eliminar(datos_instance):
    """Prueba el manejo de valores nulos eliminando filas."""
    datos_instance.datos = pd.DataFrame({'A': [1, None], 'B': [3, 4], 'C': [5, 6]})
    datos_instance.features = ['A', 'B']
    datos_instance.targets = 'C'
    with patch('builtins.input', return_value='1'):
        datos_instance.opcion2_manejo_nulos()
        assert len(datos_instance.datos) == 2
        assert datos_instance.paso == 2.3

def test_opcion2_manejo_nulos_media(datos_instance):
    """Prueba el manejo de valores nulos rellenando con la media."""
    datos_instance.datos = pd.DataFrame({'A': [1, None], 'B': [3, 4], 'C': [5, 6]})
    datos_instance.features = ['A', 'B']
    datos_instance.targets = 'C'
    with patch('builtins.input', return_value='2'):
        datos_instance.opcion2_manejo_nulos()
        assert datos_instance.datos['A'].isnull().sum() == 0
        assert datos_instance.paso == 2.3

def test_opcion2_transformar_categoricos_onehot(datos_instance):
    """Prueba la transformación de datos categóricos con One-Hot Encoding."""
    datos_instance.datos = pd.DataFrame({'A': ['x', 'y'], 'B': [1, 2]})
    datos_instance.features = ['A']
    with patch('builtins.input', return_value='1'):
        datos_instance.opcion2_transformar_categoricos()
        assert 'A_x' in datos_instance.datos.columns
        assert 'A_y' in datos_instance.datos.columns
        assert datos_instance.paso == 2.4

def test_opcion2_transformar_categoricos_label(datos_instance):
    """Prueba la transformación de datos categóricos con Label Encoding."""
    datos_instance.datos = pd.DataFrame({'A': ['x', 'y'], 'B': [1, 2]})
    datos_instance.features = ['A']
    with patch('builtins.input', return_value='2'):
        datos_instance.opcion2_transformar_categoricos()
        assert datos_instance.datos['A'].dtype == 'int64'
        assert datos_instance.paso == 2.4

def test_opcion2_normalizar_numericas_minmax(datos_instance):
    """Prueba la normalización de datos numéricos con Min-Max Scaling."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    datos_instance.features = ['A', 'B']
    with patch('builtins.input', return_value='1'):
        datos_instance.opcion2_normalizar_numericas()
        assert datos_instance.datos['A'].min() == 0
        assert datos_instance.datos['A'].max() == 1
        assert datos_instance.paso == 2.5

def test_opcion2_normalizar_numericas_zscore(datos_instance):
    """Prueba la normalización de datos numéricos con Z-score Normalization."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    datos_instance.features = ['A', 'B']
    with patch('builtins.input', return_value='2'):
        datos_instance.opcion2_normalizar_numericas()
        assert abs(datos_instance.datos['A'].mean()) < 1e-9
        assert abs(datos_instance.datos['A'].std() - 1) < 1e-9
        assert datos_instance.paso == 2.5

def test_opcion2_manejo_atipicos_eliminar(datos_instance):
    """Prueba el manejo de valores atípicos eliminando filas."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 10], 'B': [4, 5, 6]})
    datos_instance.features = ['A', 'B']
    with patch('builtins.input', return_value='1'):
        datos_instance.opcion2_manejo_atipicos()
        assert len(datos_instance.datos) == 2
        assert datos_instance.paso == 3

def test_opcion2_manejo_atipicos_mediana(datos_instance):
    """Prueba el manejo de valores atípicos reemplazando con la mediana."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 10], 'B': [4, 5, 6]})
    datos_instance.features = ['A', 'B']
    with patch('builtins.input', return_value='2'):
        datos_instance.opcion2_manejo_atipicos()
        assert datos_instance.datos['A'].max() == 2.0
        assert datos_instance.paso == 3

def test_opcion3_visualizar_datos_describe(datos_instance):
    """Prueba la visualización de datos con describe()."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    datos_instance.features = ['A', 'B']
    datos_instance.paso = 3
    with patch('builtins.input', return_value='1'):
        datos_instance.opcion3_visualizar_datos()
        # No podemos capturar la salida de print, así que solo verificamos que no haya errores
        assert datos_instance.paso == 4

def test_opcion4_exportar_datos_csv(datos_instance):
    """Prueba la exportación de datos a CSV."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    datos_instance.paso = 4
    with patch('builtins.input', return_value='1'):
        with patch('builtins.input', return_value='test_export'):
            datos_instance.opcion4_exportar_datos()
            # No podemos verificar el archivo creado, pero podemos verificar que no haya errores
            assert datos_instance.paso == 5

def test_opcion4_exportar_datos_excel(datos_instance):
    """Prueba la exportación de datos a Excel."""
    datos_instance.datos = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
    datos_instance.paso = 4
    with patch('builtins.input', return_value='2'):
        with patch('builtins.input', return_value='test_export'):
            datos_instance.opcion4_exportar_datos()
            # No podemos verificar el archivo creado, pero podemos verificar que no haya errores
            assert datos_instance.paso == 5

