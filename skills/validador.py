"""
validador.py — relación Python en el sistema de skills
YAML/JSON = estructura, Python = verifica que la estructura se cumpla.
Uso: python validador.py --schema _schemas/memorando-scjn.json --data salida.json
"""
import json, sys, pathlib

def validar(schema_path, data_path):
    import jsonschema
    schema = json.loads(pathlib.Path(schema_path).read_text(encoding="utf-8"))
    data = json.loads(pathlib.Path(data_path).read_text(encoding="utf-8"))
    jsonschema.validate(data, schema)
    print("✅ JSON válido contra schema")
    # chequeos extra del Protocolo (tratamiento especial)
    for i, h in enumerate(data.get("prueba_falla_sistemica", [])):
        if h.get("estado_verificacion") == "verificado" and "pendiente" in h.get("fuente_verificable",""):
            print(f"⚠️ fila {i}: marcado verificado pero fuente es pendiente — revisar")
    print("Validador OK")

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("uso: python validador.py <schema.json> <data.json>")
        sys.exit(1)
    validar(sys.argv[1], sys.argv[2])
