"""Pruebas con documentos sintéticos; nunca incluyen material del expediente."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

DIRECTORIO = Path(__file__).resolve().parents[1]
MODULO = DIRECTORIO / "cotejar_imagenes.py"
especificacion = importlib.util.spec_from_file_location("cotejar_imagenes", MODULO)
cotejar = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(cotejar)


@unittest.skipIf(cotejar.pymupdf is None, "PyMuPDF es una dependencia opcional")
class CotejoImagenesTest(unittest.TestCase):
    def setUp(self):
        self.temporal = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporal.cleanup)
        self.primero = Path(self.temporal.name) / "primero.pdf"
        self.segundo = Path(self.temporal.name) / "segundo.pdf"
        self.sin_imagenes = Path(self.temporal.name) / "sin.pdf"
        fitz = cotejar.pymupdf
        compartida = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 12, 10), False)
        compartida.clear_with(120)
        distinta = fitz.Pixmap(fitz.csRGB, fitz.IRect(0, 0, 12, 10), False)
        distinta.clear_with(220)
        with fitz.open() as documento:
            for _ in range(2):
                pagina = documento.new_page()
                pagina.insert_image(fitz.Rect(20, 20, 80, 70), pixmap=compartida)
            documento.save(self.primero)
        with fitz.open() as documento:
            documento.new_page().insert_image(fitz.Rect(20, 20, 80, 70), pixmap=distinta)
            documento.new_page().insert_image(fitz.Rect(20, 20, 80, 70), pixmap=compartida)
            documento.save(self.segundo)
        with fitz.open() as documento:
            documento.new_page()
            documento.save(self.sin_imagenes)

    def test_coincidencia_situa_recurso_y_no_equivale_a_pdf(self):
        resultado = cotejar.comparar(self.primero, self.segundo)
        self.assertEqual(len(resultado["coincidencias"]), 1)
        coincidencia = resultado["coincidencias"][0]
        self.assertEqual([o["pagina"] for o in coincidencia["ocurrencias_primero"]], [1, 2])
        self.assertEqual([o["pagina"] for o in coincidencia["ocurrencias_segundo"]], [2])
        self.assertEqual((coincidencia["ancho"], coincidencia["alto"]), (12, 10))
        self.assertNotEqual(resultado["primero"]["sha256_pdf"], resultado["segundo"]["sha256_pdf"])
        self.assertIn("no a los PDF completos", resultado["advertencia"])
        self.assertEqual(resultado["primero"]["errores_extraccion"], [])

    def test_filtro_y_archivo_sin_recursos(self):
        self.assertEqual(cotejar.comparar(self.primero, self.segundo, minimo_alto=11)["coincidencias"], [])
        self.assertEqual(cotejar.comparar(self.primero, self.sin_imagenes)["coincidencias"], [])
        self.assertEqual(cotejar.comparar(self.primero, self.sin_imagenes)["segundo"]["recursos_imagen_distintos"], 0)
        with self.assertRaisesRegex(ValueError, "positivos"):
            cotejar.comparar(self.primero, self.segundo, minimo_ancho=0)

    def test_cli_json_y_manejo_de_archivos_invalidos(self):
        resultado = subprocess.run(
            [sys.executable, str(MODULO), str(self.primero), str(self.segundo), "--min-alto", "5"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(json.loads(resultado.stdout)["filtros"]["minimo_alto"], 5)
        fallo = subprocess.run(
            [sys.executable, str(MODULO), str(self.primero), str(self.segundo) + ".ausente"],
            capture_output=True, text=True, check=False,
        )
        self.assertEqual(fallo.returncode, 2)
        self.assertIn("Error:", fallo.stderr)
        self.assertFalse(fallo.stdout)


if __name__ == "__main__":
    unittest.main()
