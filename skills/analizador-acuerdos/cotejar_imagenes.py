#!/usr/bin/env python3
"""Compara recursos de imagen extraídos de dos PDF locales, sin modificarlos.

Requiere PyMuPDF. Por defecto examina todas las dimensiones; los filtros
opcionales pueden reducir coincidencias triviales como escudos y logotipos.
No valida firmas, no consulta sistemas judiciales y no busca adjuntos nativos.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

try:
    import pymupdf
except ImportError:
    pymupdf = None

ADVERTENCIA = (
    "La igualdad se refiere a los bytes del recurso de imagen extraído, no a los "
    "PDF completos ni a un P7M. No prueba procedencia, fecha o transferencia; "
    "una imagen diferente puede ser una conversión de la misma. Los recursos "
    "listados pueden no estar dibujados y máscaras o superposiciones pueden "
    "cambiar lo visible: inspeccionar las páginas y conservar los originales."
)


def huella(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as archivo:
        for bloque in iter(lambda: archivo.read(1024 * 1024), b""):
            digest.update(bloque)
    return digest.hexdigest()


def inventariar(path: Path, minimo_ancho: int = 1, minimo_alto: int = 1) -> dict[str, Any]:
    """Indexa imágenes referenciadas en recursos de páginas, por bytes extraídos."""
    if pymupdf is None:
        raise RuntimeError("Se necesita PyMuPDF: python -m pip install PyMuPDF")
    if minimo_ancho < 1 or minimo_alto < 1:
        raise ValueError("Las dimensiones mínimas deben ser enteros positivos")

    sha_pdf = huella(path)
    recursos: dict[str, dict[str, Any]] = {}
    cache: dict[int, dict[str, Any]] = {}
    errores: list[dict[str, Any]] = []
    with pymupdf.open(str(path)) as documento:
        if not documento.is_pdf:
            raise ValueError(f"No es un PDF: {path}")
        if documento.needs_pass:
            raise ValueError(f"El PDF requiere contraseña: {path}")
        paginas = len(documento)
        for indice, pagina in enumerate(documento):
            vistos: set[int] = set()
            for ref in pagina.get_images(full=True):
                xref = ref[0]
                if xref in vistos:
                    continue
                vistos.add(xref)
                if xref not in cache:
                    try:
                        extraida = documento.extract_image(xref)
                        if not extraida or not extraida.get("image"):
                            raise ValueError("La imagen no pudo extraerse")
                        contenido = extraida["image"]
                        cache[xref] = {
                            "sha256": hashlib.sha256(contenido).hexdigest(),
                            "ancho": extraida["width"],
                            "alto": extraida["height"],
                            "formato": extraida["ext"],
                            "bytes_extraidos": len(contenido),
                        }
                    except (RuntimeError, ValueError, KeyError) as error:
                        errores.append({"pagina": indice + 1, "xref": xref, "error": str(error)})
                        continue
                imagen = cache[xref]
                if imagen["ancho"] < minimo_ancho or imagen["alto"] < minimo_alto:
                    continue
                digest = imagen["sha256"]
                recurso = recursos.setdefault(digest, {**imagen, "ocurrencias": []})
                recurso["ocurrencias"].append({"pagina": indice + 1, "xref": xref})
    return {
        "archivo": str(path),
        "sha256_pdf": sha_pdf,
        "paginas": paginas,
        "recursos": recursos,
        "errores_extraccion": errores,
    }


def comparar(primero: Path, segundo: Path, minimo_ancho: int = 1, minimo_alto: int = 1) -> dict[str, Any]:
    a = inventariar(primero, minimo_ancho, minimo_alto)
    b = inventariar(segundo, minimo_ancho, minimo_alto)
    coincidencias = []
    for digest in sorted(a["recursos"].keys() & b["recursos"].keys()):
        imagen_a = a["recursos"][digest]
        coincidencias.append({
            "sha256": digest,
            "ancho": imagen_a["ancho"],
            "alto": imagen_a["alto"],
            "formato": imagen_a["formato"],
            "bytes_extraidos": imagen_a["bytes_extraidos"],
            "ocurrencias_primero": imagen_a["ocurrencias"],
            "ocurrencias_segundo": b["recursos"][digest]["ocurrencias"],
        })
    for inventario in (a, b):
        inventario["recursos_imagen_distintos"] = len(inventario.pop("recursos"))
    return {
        "advertencia": ADVERTENCIA,
        "filtros": {"minimo_ancho": minimo_ancho, "minimo_alto": minimo_alto},
        "primero": a,
        "segundo": b,
        "coincidencias": coincidencias,
    }


def positivo(valor: str) -> int:
    numero = int(valor)
    if numero < 1:
        raise argparse.ArgumentTypeError("debe ser un entero positivo")
    return numero


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("primero", type=Path, help="Primer PDF local")
    parser.add_argument("segundo", type=Path, help="Segundo PDF local")
    parser.add_argument("--min-ancho", type=positivo, default=1, help="Ancho mínimo en píxeles")
    parser.add_argument("--min-alto", type=positivo, default=1, help="Alto mínimo en píxeles")
    args = parser.parse_args(argv)
    try:
        resultado = comparar(args.primero, args.segundo, args.min_ancho, args.min_alto)
    except (OSError, RuntimeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(json.dumps(resultado, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
