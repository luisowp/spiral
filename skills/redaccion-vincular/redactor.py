#!/usr/bin/env python3
"""Ensambla un mapa de redacción a partir de datos declarados, sin inferir hechos.

Uso:
  python redactor.py caso.json --via familiar

No consulta Drive, no autentica fuentes, no calcula plazos ni decide procedencia.
El resultado es un borrador de trabajo: exige actualización y revisión humana.
"""
from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any
from urllib.parse import urlsplit

VIAS = frozenset({"familiar", "amparo", "penal", "peticion-cidh", "cautelares-cidh"})
ESTADOS = frozenset({"documento", "relato", "hipotesis", "pendiente"})
TIPOS_FUENTE = frozenset({"original", "reproduccion", "transcripcion", "relato", "analisis"})
ID = re.compile(r"^[A-Za-z0-9_-]{1,32}$")
ADVERTENCIA = (
    "BORRADOR DE TRABAJO, NO LISTO PARA PRESENTAR. Los datos son declarados; "
    "esta herramienta no verifica hechos, fuentes, plazos ni procedencia. "
    "Actualizar el corte y revisar actuaciones, medidas vigentes y seguridad."
)


def _objeto(valor: Any, donde: str) -> dict[str, Any]:
    if not isinstance(valor, dict):
        raise ValueError(f"{donde}: se requiere un objeto")
    return valor


def _texto(obj: dict[str, Any], campo: str, donde: str) -> str:
    valor = obj.get(campo)
    if not isinstance(valor, str) or not valor.strip():
        raise ValueError(f"{donde}: '{campo}' debe ser texto no vacío")
    return valor.strip()


def _id(obj: dict[str, Any], donde: str) -> str:
    valor = _texto(obj, "id", donde)
    if not ID.fullmatch(valor):
        raise ValueError(f"{donde}: ID inválido")
    return valor


def _lista(obj: dict[str, Any], campo: str, donde: str, *, minimo: int = 1) -> list[Any]:
    valor = obj.get(campo)
    if not isinstance(valor, list) or len(valor) < minimo:
        raise ValueError(f"{donde}: '{campo}' debe ser una lista con al menos {minimo} elementos")
    return valor


def _lista_texto(obj: dict[str, Any], campo: str, donde: str, *, minimo: int = 1) -> list[str]:
    valores = _lista(obj, campo, donde, minimo=minimo)
    if any(not isinstance(v, str) or not v.strip() for v in valores):
        raise ValueError(f"{donde}: '{campo}' debe contener textos no vacíos")
    return [v.strip() for v in valores]


def _url(obj: dict[str, Any], campo: str, donde: str, *, obligatoria: bool = False) -> str:
    valor = obj.get(campo, "")
    if not isinstance(valor, str):
        raise ValueError(f"{donde}: '{campo}' debe ser texto")
    valor = valor.strip()
    if not valor and not obligatoria:
        return ""
    partes = urlsplit(valor)
    if partes.scheme != "https" or not partes.netloc or any(c.isspace() or c in '<>"' for c in valor):
        raise ValueError(f"{donde}: '{campo}' debe ser URL https válida")
    return valor


def _indexar(items: list[Any], nombre: str) -> dict[str, dict[str, Any]]:
    resultado: dict[str, dict[str, Any]] = {}
    for i, dato in enumerate(items):
        donde = f"{nombre}[{i}]"
        obj = _objeto(dato, donde)
        clave = _id(obj, donde)
        if clave in resultado:
            raise ValueError(f"{donde}: ID duplicado '{clave}'")
        resultado[clave] = obj
    return resultado


def _referencias(obj: dict[str, Any], campo: str, donde: str, destino: dict[str, Any], *, minimo: int = 1) -> list[str]:
    valores = _lista_texto(obj, campo, donde, minimo=minimo)
    for valor in valores:
        if valor not in destino:
            raise ValueError(f"{donde}: referencia '{valor}' no existe en {campo}")
    if len(set(valores)) != len(valores):
        raise ValueError(f"{donde}: referencia duplicada en '{campo}'")
    return valores


def validar(datos: Any) -> dict[str, Any]:
    """Valida estructura y referencias declaradas, no su autenticidad ni contenido."""
    datos = _objeto(datos, "entrada")
    if type(datos.get("version")) is not int or datos["version"] != 1:
        raise ValueError("entrada: 'version' debe ser el entero 1")
    _texto(datos, "titulo", "entrada")
    corte = _texto(datos, "fecha_corte", "entrada")
    try:
        if date.fromisoformat(corte).isoformat() != corte:
            raise ValueError
    except ValueError as exc:
        raise ValueError("entrada: 'fecha_corte' debe tener formato AAAA-MM-DD y ser fecha válida") from exc

    fuentes = _indexar(_lista(datos, "fuentes", "entrada"), "fuentes")
    for clave, fuente in fuentes.items():
        donde = f"fuente {clave}"
        if _texto(fuente, "tipo", donde) not in TIPOS_FUENTE:
            raise ValueError(f"{donde}: tipo de fuente inválido")
        for campo in ("titulo", "ubicacion", "limite"):
            _texto(fuente, campo, donde)
        _url(fuente, "url", donde)

    hechos = _indexar(_lista(datos, "hechos", "entrada"), "hechos")
    for clave, hecho in hechos.items():
        donde = f"hecho {clave}"
        estado = _texto(hecho, "estado", donde)
        if estado not in ESTADOS:
            raise ValueError(f"{donde}: estado inválido")
        _texto(hecho, "contenido", donde)
        _texto(hecho, "limite", donde)
        refs = _referencias(hecho, "fuentes", donde, fuentes, minimo=0 if estado == "pendiente" else 1)
        if estado == "documento" and not any(fuentes[r]["tipo"] in {"original", "reproduccion", "transcripcion"} for r in refs):
            raise ValueError(f"{donde}: 'documento' requiere fuente documental, reproducción o transcripción")

    criterios = _indexar(_lista(datos, "criterios", "entrada"), "criterios")
    for clave, criterio in criterios.items():
        donde = f"criterio {clave}"
        for campo in ("cita", "uso", "limite"):
            _texto(criterio, campo, donde)
        _url(criterio, "url", donde, obligatoria=True)

    bloques = _indexar(_lista(datos, "bloques", "entrada"), "bloques")
    for clave, bloque in bloques.items():
        donde = f"bloque {clave}"
        if _texto(bloque, "via", donde) not in VIAS:
            raise ValueError(f"{donde}: vía inválida")
        for campo in ("pregunta", "argumento"):
            _texto(bloque, campo, donde)
        _referencias(bloque, "hechos", donde, hechos)
        _referencias(bloque, "criterios", donde, criterios)
        _lista_texto(bloque, "peticiones", donde)
        _lista_texto(bloque, "verificaciones", donde)
    return {"datos": datos, "fuentes": fuentes, "hechos": hechos, "criterios": criterios, "bloques": bloques}


def _linea(valor: str) -> str:
    # Los saltos embebidos no deben crear títulos o listas Markdown adicionales.
    return " ".join(valor.split()).replace("\\", "\\\\").replace("|", "\\|")


def a_markdown(datos: Any, via: str) -> str:
    estructura = validar(datos)
    if via not in VIAS:
        raise ValueError("Vía desconocida")
    bloques = [b for b in estructura["bloques"].values() if b["via"] == via]
    if not bloques:
        raise ValueError(f"No hay bloques declarados para la vía '{via}'")
    cabecera = estructura["datos"]
    salida = [
        f"# {_linea(cabecera['titulo'])}", "", f"**Vía:** {_linea(via)} · **Corte declarado:** {_linea(cabecera['fecha_corte'])}",
        "", f"**{ADVERTENCIA}**", "",
    ]
    fuentes_usadas: set[str] = set()
    for bloque in bloques:
        salida.extend([
            f"## {_linea(bloque['pregunta'])}", "",
            "### Argumento propuesto en primera persona", "", _linea(bloque["argumento"]), "",
            "### Hechos declarados y límites", "",
        ])
        for ref in bloque["hechos"]:
            hecho = estructura["hechos"][ref]
            fuentes_usadas.update(hecho["fuentes"])
            ids = ", ".join(hecho["fuentes"]) if hecho["fuentes"] else "sin fuente indicada"
            salida.append(f"- **{ref} — {_linea(hecho['estado'])}:** {_linea(hecho['contenido'])} "
                          f"Fuentes: {ids}. **Límite:** {_linea(hecho['limite'])}")
        salida.extend(["", "### Referencias jurídicas y diferencia", ""])
        for ref in bloque["criterios"]:
            criterio = estructura["criterios"][ref]
            url = _url(criterio, "url", f"criterio {ref}", obligatoria=True).replace(")", "%29").replace("(", "%28")
            salida.append(f"- **{ref}:** {_linea(criterio['cita'])}. <{url}> "
                          f"**Uso:** {_linea(criterio['uso'])} **Límite:** {_linea(criterio['limite'])}")
        salida.extend(["", "### Medidas o solicitudes por adaptar", ""])
        salida.extend(f"- {_linea(item)}" for item in bloque["peticiones"])
        salida.extend(["", "### Verificaciones imprescindibles", ""])
        salida.extend(f"- {_linea(item)}" for item in bloque["verificaciones"])
        salida.append("")
    salida.extend(["## Fuentes declaradas de esta vía", ""])
    for ref, fuente in estructura["fuentes"].items():
        if ref not in fuentes_usadas:
            continue
        url = _url(fuente, "url", f"fuente {ref}")
        enlace = f" <{url.replace(')', '%29').replace('(', '%28')}>" if url else ""
        salida.append(f"- **{ref} — {_linea(fuente['tipo'])}:** {_linea(fuente['titulo'])}; "
                      f"{_linea(fuente['ubicacion'])}.{enlace} **Límite:** {_linea(fuente['limite'])}")
    return "\n".join(salida) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="JSON local con fuentes y hechos declarados")
    parser.add_argument("--via", choices=sorted(VIAS), required=True, help="Foro a separar en el borrador")
    args = parser.parse_args(argv)
    try:
        with args.entrada.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)
        resultado = a_markdown(datos, args.via)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    print(resultado, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
