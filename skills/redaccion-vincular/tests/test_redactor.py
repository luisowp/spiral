"""Pruebas de forma con datos ficticios; no evalúan hechos ni fondo legal."""
from copy import deepcopy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

DIRECTORIO = Path(__file__).resolve().parents[1]
MODULO = DIRECTORIO / "redactor.py"
EJEMPLO = DIRECTORIO / "ejemplo-sintetico.json"
especificacion = importlib.util.spec_from_file_location("redactor", MODULO)
redactor = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(redactor)


def ejemplo():
    return json.loads(EJEMPLO.read_text(encoding="utf-8"))


class RedactorTest(unittest.TestCase):
    def test_ejemplo_estructura_y_cada_via(self):
        datos = ejemplo()
        redactor.validar(datos)
        for via in redactor.VIAS:
            with self.subTest(via=via):
                salida = redactor.a_markdown(datos, via)
                self.assertIn("BORRADOR DE TRABAJO, NO LISTO PARA PRESENTAR", salida)
                self.assertIn(f"**Vía:** {via}", salida)
                self.assertIn("Referencias jurídicas y diferencia", salida)
                self.assertIn("Verificaciones imprescindibles", salida)
                self.assertIn("Fuentes declaradas de esta vía", salida)
                self.assertIn("**Límite:**", salida)

    def test_ejemplo_y_referencias_son_ficticios(self):
        datos = ejemplo()
        self.assertIn("ficticio", datos["titulo"].lower())
        for criterio in datos["criterios"]:
            self.assertTrue(criterio["url"].startswith("https://example.org/"))
            self.assertIn("no es fuente jurídica real", criterio["limite"].lower())

    def test_vias_no_mezclan_hechos_ni_criterios(self):
        datos = ejemplo()
        familiar = redactor.a_markdown(datos, "familiar")
        penal = redactor.a_markdown(datos, "penal")
        cautelares = redactor.a_markdown(datos, "cautelares-cidh")
        peticion = redactor.a_markdown(datos, "peticion-cidh")
        self.assertIn("H1 — documento", familiar)
        self.assertNotIn("H6 — relato", familiar)
        self.assertIn("H6 — relato", penal)
        self.assertNotIn("H1 — documento", penal)
        self.assertIn("J5", cautelares)
        self.assertNotIn("J4", cautelares)
        self.assertIn("J4", peticion)
        self.assertNotIn("J5", peticion)

    def test_recepcion_no_equivale_a_ejecucion(self):
        salida = redactor.a_markdown(ejemplo(), "familiar")
        self.assertIn("Recepción no equivale a decisión o cumplimiento", salida)
        self.assertIn("No consta no significa que el evento no ocurrió", salida)

    def test_relato_e_hipotesis_no_son_documentos(self):
        salida = redactor.a_markdown(ejemplo(), "amparo")
        self.assertIn("H3 — hipotesis", salida)
        self.assertIn("requieren comprobación", salida)
        self.assertIn("H5 — documento", salida)

    def test_fuente_documental_requiere_tipo_compatible(self):
        datos = ejemplo()
        datos["hechos"][0]["fuentes"] = ["F2"]
        with self.assertRaisesRegex(ValueError, "requiere fuente documental"):
            redactor.validar(datos)

    def test_fuentes_requeridas_salvo_pendiente(self):
        datos = ejemplo()
        datos["hechos"][0]["fuentes"] = []
        with self.assertRaisesRegex(ValueError, "al menos 1"):
            redactor.validar(datos)
        datos = ejemplo()
        self.assertIn("sin fuente indicada", redactor.a_markdown(datos, "familiar"))

    def test_fuentes_y_referencias_inexistentes(self):
        for lista, campo in [("hechos", "fuentes"), ("bloques", "hechos"), ("bloques", "criterios")]:
            datos = ejemplo()
            datos[lista][0][campo] = ["inexistente"]
            with self.subTest(lista=lista, campo=campo), self.assertRaisesRegex(ValueError, "no existe"):
                redactor.validar(datos)

    def test_referencias_duplicadas_no_se_aceptan(self):
        datos = ejemplo()
        datos["bloques"][0]["hechos"] = ["H1", "H1"]
        with self.assertRaisesRegex(ValueError, "duplicada"):
            redactor.validar(datos)

    def test_ids_duplicados_no_se_aceptan(self):
        datos = ejemplo()
        datos["fuentes"][1]["id"] = datos["fuentes"][0]["id"]
        with self.assertRaisesRegex(ValueError, "duplicado"):
            redactor.validar(datos)

    def test_ids_invalidos_no_se_aceptan(self):
        datos = ejemplo()
        datos["fuentes"][0]["id"] = "id con espacios"
        with self.assertRaisesRegex(ValueError, "ID inválido"):
            redactor.validar(datos)

    def test_fecha_debe_ser_real_e_iso(self):
        for fecha in ["2040-02-30", "01/01/2040", "", "2040-1-1"]:
            datos = ejemplo()
            datos["fecha_corte"] = fecha
            with self.subTest(fecha=fecha), self.assertRaises(ValueError):
                redactor.validar(datos)

    def test_version_requiere_entero_uno(self):
        for valor in [True, 1.0, "1", 2, None]:
            datos = ejemplo()
            datos["version"] = valor
            with self.subTest(valor=valor), self.assertRaisesRegex(ValueError, "versión|version"):
                redactor.validar(datos)

    def test_estado_tipo_y_via_invalidos(self):
        for lista, clave in [("hechos", "estado"), ("fuentes", "tipo"), ("bloques", "via")]:
            datos = ejemplo()
            datos[lista][0][clave] = "no-existe"
            with self.subTest(lista=lista), self.assertRaises(ValueError):
                redactor.validar(datos)

    def test_campos_obligatorios_no_pueden_vaciarse(self):
        for lista, campo in [("fuentes", "titulo"), ("hechos", "contenido"), ("criterios", "limite"), ("bloques", "argumento")]:
            datos = ejemplo()
            datos[lista][0][campo] = "  "
            with self.subTest(lista=lista, campo=campo), self.assertRaises(ValueError):
                redactor.validar(datos)

    def test_listas_vacias_invalidas(self):
        for lista in ["fuentes", "hechos", "criterios", "bloques"]:
            datos = ejemplo()
            datos[lista] = []
            with self.subTest(lista=lista), self.assertRaises(ValueError):
                redactor.validar(datos)

    def test_url_fuente_opcional_y_criterio_obligatoria(self):
        datos = ejemplo()
        datos["fuentes"][0]["url"] = ""
        redactor.validar(datos)
        for url in ["", "http://example.org/", "https://example.org/a b"]:
            datos = ejemplo()
            datos["criterios"][0]["url"] = url
            with self.subTest(url=url), self.assertRaises(ValueError):
                redactor.validar(datos)

    def test_no_via_sin_bloques_y_no_mutacion(self):
        datos = ejemplo()
        original = deepcopy(datos)
        redactor.a_markdown(datos, "familiar")
        self.assertEqual(datos, original)
        datos["bloques"] = [b for b in datos["bloques"] if b["via"] != "amparo"]
        with self.assertRaisesRegex(ValueError, "No hay bloques"):
            redactor.a_markdown(datos, "amparo")
        with self.assertRaisesRegex(ValueError, "Vía desconocida"):
            redactor.a_markdown(datos, "inexistente")

    def test_textos_no_crean_saltos_de_seccion(self):
        datos = ejemplo()
        datos["bloques"][0]["argumento"] = "Texto | otro\n# título no deseado"
        salida = redactor.a_markdown(datos, "familiar")
        self.assertIn("Texto \\| otro # título no deseado", salida)
        self.assertNotIn("\n# título no deseado", salida)

    def test_fuentes_no_usadas_no_aparecen(self):
        salida = redactor.a_markdown(ejemplo(), "penal")
        self.assertIn("F2 — relato", salida)
        self.assertNotIn("F1 — reproduccion", salida)

    def test_cli_y_error_entrada(self):
        proceso = subprocess.run([sys.executable, str(MODULO), str(EJEMPLO), "--via", "amparo"], capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        self.assertIn("BORRADOR DE TRABAJO", proceso.stdout)
        proceso = subprocess.run([sys.executable, str(MODULO), "/ruta/no/existe.json", "--via", "amparo"], capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 2)
        self.assertIn("Error:", proceso.stderr)
        self.assertEqual(proceso.stdout, "")

    def test_cli_exige_via_explicita(self):
        proceso = subprocess.run([sys.executable, str(MODULO), str(EJEMPLO)], capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 2)
        self.assertIn("--via", proceso.stderr)


if __name__ == "__main__":
    unittest.main()
