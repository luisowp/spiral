#!/usr/bin/env python3
"""Comparación descriptiva de nombres numéricos, sin asignar significado jurídico.

Uso con identificadores completamente ficticios (desde la raíz):
    python skills/analizador-acuerdos/nomenclatura.py --referencia 12345678 \
      12340000123456780001110003330015.pdf \
      12340000876543210001110002220003.pdf

Solo acepta un nombre de archivo (no una ruta), con 32 o 33 dígitos ASCII y
extensión .pdf opcional. El corte es una hipótesis de trabajo; no se ha cotejado
un catálogo oficial. No consulta archivos, sistemas, datos personales ni Drive.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from typing import Any

PATRON = re.compile(r"^([0-9]{4})([0-9]{4})([0-9]{8})([0-9]{6})([0-9]{6})([0-9]{4,5})(?:\.pdf)?$", re.IGNORECASE)
BLOQUE_OCHO = re.compile(r"^[0-9]{8}$")
ADVERTENCIA = (
    "Corte descriptivo no certificado: las posiciones y su significado no "
    "están acreditados por un diccionario oficial. Una diferencia no prueba "
    "por sí sola identidad de NEUN, error, manipulación ni falsedad."
)


def descomponer(nombre: str) -> dict[str, str]:
    """Conserva ceros iniciales y evita inventar un significado para los bloques."""
    if not isinstance(nombre, str):
        raise ValueError("El nombre debe ser texto")
    hallazgo = PATRON.fullmatch(nombre)
    if not hallazgo:
        raise ValueError("Se requieren 32 o 33 dígitos ASCII, con .pdf opcional; no se aceptan rutas")
    claves = ("1_4", "5_8", "9_16", "17_22", "23_28", "29_final")
    return dict(zip(claves, hallazgo.groups()))


def comparar(nombres: list[str], referencia: str | None = None) -> dict[str, Any]:
    """Compara exclusivamente el bloque 9–16 con una referencia suministrada."""
    if not isinstance(nombres, list) or not nombres:
        raise ValueError("Se requiere al menos un nombre")
    if referencia is not None and (not isinstance(referencia, str) or not BLOQUE_OCHO.fullmatch(referencia)):
        raise ValueError("La referencia debe ser una cadena de 8 dígitos ASCII")
    filas: list[dict[str, Any]] = []
    for nombre in nombres:
        bloques = descomponer(nombre)
        fila: dict[str, Any] = {"nombre": nombre, "bloques_por_posicion": bloques}
        if referencia is not None:
            fila["difiere_de_referencia_en_9_16"] = bloques["9_16"] != referencia
        filas.append(fila)
    return {"advertencia": ADVERTENCIA, "referencia_de_usuario": referencia, "nombres": filas}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("nombres", nargs="+", help="Nombres numéricos, no rutas ni URL")
    parser.add_argument("--referencia", help="Bloque de 8 dígitos con que comparar las posiciones 9–16")
    args = parser.parse_args(argv)
    try:
        resultado = comparar(args.nombres, args.referencia)
    except ValueError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
