"""Pruebas sin dependencias externas para grafos completamente ficticios."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest

DIRECTORIO = Path(__file__).resolve().parents[1]
MODULO = DIRECTORIO / "trazabilidad.py"
EJEMPLO = DIRECTORIO / "ejemplo-trazabilidad-sintetico.json"
especificacion = importlib.util.spec_from_file_location("trazabilidad", MODULO)
trazabilidad = importlib.util.module_from_spec(especificacion)
especificacion.loader.exec_module(trazabilidad)


def grafo():
    return {
        "version": 1,
        "nodos": [
            {"id": "a", "descripcion": "Inicio"},
            {"id": "b", "descripcion": "Intermedio"},
            {"id": "c", "descripcion": "Resultado"},
            {"id": "aislado", "descripcion": "Sin relación declarada"},
        ],
        "conexiones": [
            {"origen": "a", "destino": "b", "estado": "observado", "detalle": "La fuente lo reporta", "fuente": "acuse ficticio"},
            {"origen": "b", "destino": "c", "estado": "pendiente", "detalle": "No consta la remisión", "verificacion_pendiente": "Pedir boleta"},
        ],
    }


class TrazabilidadTest(unittest.TestCase):
    def test_recorrido_inverso_conserva_estados_y_fuentes(self):
        resultado = trazabilidad.reconstruir(grafo(), "c")
        self.assertEqual([(c["origen"], c["destino"]) for c in resultado["conexiones"]], [("b", "c"), ("a", "b")])
        self.assertEqual([c["estado"] for c in resultado["conexiones"]], ["pendiente", "observado"])
        self.assertEqual(resultado["conexiones"][1]["fuente"], "acuse ficticio")
        self.assertEqual({n["id"] for n in resultado["nodos_alcanzados"]}, {"a", "b", "c"})
        self.assertIn("no son hechos", resultado["advertencia"])

    def test_objetivo_aislado_no_inventa_cadena_rota(self):
        resultado = trazabilidad.reconstruir(grafo(), "aislado")
        self.assertEqual(resultado["conexiones"], [])
        self.assertIn("no prueba su inexistencia", trazabilidad.a_markdown(resultado))

    def test_ciclo_termina_y_no_descarta_conexiones(self):
        datos = grafo()
        datos["conexiones"].append({"origen": "c", "destino": "a", "estado": "hipotesis", "detalle": "Relación a verificar"})
        resultado = trazabilidad.reconstruir(datos, "c")
        self.assertEqual(len(resultado["conexiones"]), 3)
        self.assertEqual(resultado["conexiones"][2]["estado"], "hipotesis")

    def test_version_requiere_entero(self):
        for version in [True, 1.0, "1", 2, None]:
            datos = grafo()
            datos["version"] = version
            with self.subTest(version=version), self.assertRaisesRegex(ValueError, "versión"):
                trazabilidad.validar(datos)

    def test_datos_mal_formados(self):
        casos = []
        datos = grafo(); datos["nodos"].append({"id": "a", "descripcion": "Duplicado"}); casos.append((datos, "duplicado"))
        datos = grafo(); datos["conexiones"][0]["origen"] = "inexistente"; casos.append((datos, "no existe"))
        datos = grafo(); datos["conexiones"][0]["estado"] = "probado"; casos.append((datos, "estado"))
        datos = grafo(); datos["conexiones"][0]["fuente"] = " "; casos.append((datos, "requiere identificar su fuente"))
        datos = grafo(); datos["conexiones"][0]["estado"] = "relatado"; datos["conexiones"][0]["fuente"] = ""; casos.append((datos, "requiere identificar su fuente"))
        datos = grafo(); datos["conexiones"][0]["detalle"] = 123; casos.append((datos, "detalle"))
        for datos, patron in casos:
            with self.subTest(patron=patron), self.assertRaisesRegex(ValueError, patron):
                trazabilidad.validar(datos)
        with self.assertRaisesRegex(ValueError, "objetivo"):
            trazabilidad.reconstruir(grafo(), "inexistente")

    def test_markdown_escapa_tablas_y_saltos(self):
        datos = grafo()
        datos["conexiones"][1]["detalle"] = "uno | dos\notra línea"
        tabla = trazabilidad.a_markdown(trazabilidad.reconstruir(datos, "c"))
        self.assertIn("uno \\| dos otra línea", tabla)

    def test_ejemplo_y_cli_json(self):
        proceso = subprocess.run([sys.executable, str(MODULO), str(EJEMPLO), "--objetivo", "permiso", "--formato", "json"], capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 0, proceso.stderr)
        resultado = json.loads(proceso.stdout)
        alcanzados = {n["id"] for n in resultado["nodos_alcanzados"]}
        self.assertTrue({"escrito", "acuse", "turno", "expediente", "permiso"} <= alcanzados)
        self.assertNotIn("notificacion", alcanzados)
        self.assertIn("hipotesis", {c["estado"] for c in resultado["conexiones"]})
        self.assertIn("pendiente", {c["estado"] for c in resultado["conexiones"]})

    def test_permiso_no_demuestra_notificacion(self):
        datos = json.loads(EJEMPLO.read_text(encoding="utf-8"))
        resultado = trazabilidad.reconstruir(datos, "notificacion")
        relaciones = {(c["origen"], c["destino"]): c for c in resultado["conexiones"]}
        self.assertEqual(relaciones[("permiso", "notificacion")]["estado"], "pendiente")
        self.assertIn("no acredita", relaciones[("permiso", "notificacion")]["detalle"])

    def test_acuse_no_demuestra_identidad_de_anexos(self):
        datos = json.loads(EJEMPLO.read_text(encoding="utf-8"))
        resultado = trazabilidad.reconstruir(datos, "permiso")
        relaciones = {(c["origen"], c["destino"]): c for c in resultado["conexiones"]}
        self.assertEqual(relaciones[("anexos", "acuse")]["estado"], "hipotesis")
        self.assertIn("no acredita identidad", relaciones[("anexos", "acuse")]["detalle"])

    def test_turno_no_demuestra_integracion(self):
        datos = json.loads(EJEMPLO.read_text(encoding="utf-8"))
        resultado = trazabilidad.reconstruir(datos, "permiso")
        relaciones = {(c["origen"], c["destino"]): c for c in resultado["conexiones"]}
        self.assertEqual(relaciones[("turno", "expediente")]["estado"], "pendiente")
        self.assertEqual(relaciones[("expediente", "permiso")]["estado"], "pendiente")

    def test_cli_devuelve_error_si_falta_archivo(self):
        proceso = subprocess.run([sys.executable, str(MODULO), "/ruta/no/existe.json", "--objetivo", "permiso"], capture_output=True, text=True)
        self.assertEqual(proceso.returncode, 2)
        self.assertIn("Error:", proceso.stderr)
        self.assertEqual(proceso.stdout, "")


if __name__ == "__main__":
    unittest.main()
