
import unittest
from unittest.mock import patch
import pandas as pd
from menu import mostrar_datos, obtener_indice_valido

class TestMenu(unittest.TestCase):
    def setUp(self):
        # Cambia esto por las columnas reales de tu DataFrame
        self.datos = pd.DataFrame({
            "PassengerId": [5, 2],  
            "Cabin": ["NaN", "C85"]
        })

    def test_mostrar_datos(self):
        with patch("sys.stdout") as mock_stdout:
            mostrar_datos(self.datos, "test.csv")
            self.assertTrue(mock_stdout.write.called)  # Verifica que imprime algo

    def test_obtener_indice_valido(self):
        with patch("builtins.input", return_value="1"):
            self.assertEqual(obtener_indice_valido("Seleccione una columna:", 2), 0)

        with patch("builtins.input", return_value="3"):  # Fuera de rango
            with self.assertRaises(ValueError):
                obtener_indice_valido("Seleccione una columna:", 2)

if __name__ == "__main__":
    unittest.main()