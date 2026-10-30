"""Pruebas con identificadores sintéticos; no certifican sistemas ni expedientes."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

DIRECTORIO = Path(__file__).resolve().parents[1]
MODULO = DIRECTORIO / "nomenclatura.py"
especificacion = importlib.util.spec_from_file_location("nomenclatura", MODULO)
nomenclatura = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(nomenclatura)


def nombre(identificador="87654321", registro="000222", cola="0003", extension="pdf"):
    return f"12340000{identificador}000111{registro}{cola}.{extension}"


class NomenclaturaTest(unittest.TestCase):
    def test_corte_preserva_ceros_y_no_infiere_neun(self):
        archivo = nombre()
        self.assertEqual(nomenclatura.descomponer(archivo), {
            "1_4": "1234", "5_8": "0000", "9_16": "87654321",
            "17_22": "000111", "23_28": "000222", "29_final": "0003",
        })
        resultado = nomenclatura.comparar([archivo], "12345678")
        self.assertTrue(resultado["nombres"][0]["difiere_de_referencia_en_9_16"])
        self.assertIn("no prueba", resultado["advertencia"])
        self.assertNotIn("NEUN", resultado["nombres"][0]["bloques_por_posicion"])

    def test_comparacion_explicita(self):
        archivos = [nombre("12345678", "000333", "0001"), nombre("12345678", "000333", "0002")]
        filas = nomenclatura.comparar(archivos, "12345678")["nombres"]
        self.assertEqual([f["bloques_por_posicion"]["23_28"] for f in filas], ["000333", "000333"])
        self.assertEqual([f["bloques_por_posicion"]["29_final"] for f in filas], ["0001", "0002"])
        self.assertFalse(any(f["difiere_de_referencia_en_9_16"] for f in filas))
        self.assertNotIn("difiere_de_referencia_en_9_16", nomenclatura.comparar(archivos)["nombres"][0])

    def test_cola_de_cinco_digitos_no_se_trunca(self):
        bloques = nomenclatura.descomponer(nombre(registro="000444", cola="00123"))
        self.assertEqual(bloques["23_28"], "000444")
        self.assertEqual(bloques["29_final"], "00123")

    def test_rechaza_formato_no_reconocido_y_no_interpreta_rutas(self):
        for archivo in ("123.pdf", "/tmp/" + nombre(), nombre(extension="p7m"), "1234 0000", ""):
            with self.subTest(archivo=archivo), self.assertRaises(ValueError):
                nomenclatura.descomponer(archivo)
        with self.assertRaises(ValueError):
            nomenclatura.comparar([], "12345678")
        with self.assertRaises(ValueError):
            nomenclatura.comparar([nombre()], "1234567")

    def test_cli_json_y_error_sin_resultado_parcial(self):
        archivo = nombre(extension="PDF")
        p = subprocess.run([sys.executable, str(MODULO), "--referencia", "12345678", archivo], text=True, capture_output=True)
        self.assertEqual(p.returncode, 0, p.stderr)
        self.assertEqual(json.loads(p.stdout)["nombres"][0]["bloques_por_posicion"]["9_16"], "87654321")
        p = subprocess.run([sys.executable, str(MODULO), archivo, "mal.pdf"], text=True, capture_output=True)
        self.assertEqual(p.returncode, 2)
        self.assertIn("Error:", p.stderr)
        self.assertEqual(p.stdout, "")


if __name__ == "__main__":
    unittest.main()
