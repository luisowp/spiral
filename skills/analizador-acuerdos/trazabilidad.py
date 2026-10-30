#!/usr/bin/env python3
"""Reconstrucción inversa de relaciones declaradas; no consulta ni autentica fuentes.

Uso:
    python trazabilidad.py entrada.json --objetivo ID [--formato md|json]

Las conexiones, su clasificación y sus fuentes las introduce una persona. El
programa únicamente las valida y recorre hacia atrás: no descubre relaciones,
no concluye contradicciones jurídicas y no prueba que las fuentes sean ciertas.
"""
from __future__ import annotations

import argparse
from collections import deque
import json
from pathlib import Path
import sys
from typing import Any

ESTADOS = frozenset({"observado", "relatado", "hipotesis", "pendiente"})
ADVERTENCIA = (
    "Recorrido de conexiones declaradas: una observación indica lo que muestra "
    "su fuente, no que el hecho esté autenticado. Las hipótesis y los pendientes "
    "no son hechos; una conexión ausente no demuestra que no haya ocurrido."
)


def _texto(objeto: dict[str, Any], clave: str, ubicacion: str, *, obligatorio: bool = True) -> str:
    valor = objeto.get(clave, "")
    if not isinstance(valor, str) or (obligatorio and not valor.strip()):
        raise ValueError(f"{ubicacion}: '{clave}' debe ser texto{' no vacío' if obligatorio else ''}")
    return valor.strip()


def validar(datos: Any) -> tuple[dict[str, dict[str, str]], list[dict[str, str]]]:
    """Valida IDs, referencias y clasificaciones, sin verificar hechos o fuentes."""
    if not isinstance(datos, dict):
        raise ValueError("La entrada debe ser un objeto JSON")
    if type(datos.get("version")) is not int or datos["version"] != 1:
        raise ValueError("La versión de entrada debe ser el entero 1")
    nodos_raw, conexiones_raw = datos.get("nodos"), datos.get("conexiones")
    if not isinstance(nodos_raw, list) or not nodos_raw:
        raise ValueError("'nodos' debe ser una lista no vacía")
    if not isinstance(conexiones_raw, list):
        raise ValueError("'conexiones' debe ser una lista")

    nodos: dict[str, dict[str, str]] = {}
    for i, nodo in enumerate(nodos_raw):
        ubicacion = f"nodos[{i}]"
        if not isinstance(nodo, dict):
            raise ValueError(f"{ubicacion} debe ser un objeto")
        identificador = _texto(nodo, "id", ubicacion)
        if identificador in nodos:
            raise ValueError(f"{ubicacion}: ID duplicado '{identificador}'")
        nodos[identificador] = {
            "id": identificador,
            "descripcion": _texto(nodo, "descripcion", ubicacion),
        }

    conexiones: list[dict[str, str]] = []
    for i, conexion in enumerate(conexiones_raw):
        ubicacion = f"conexiones[{i}]"
        if not isinstance(conexion, dict):
            raise ValueError(f"{ubicacion} debe ser un objeto")
        origen = _texto(conexion, "origen", ubicacion)
        destino = _texto(conexion, "destino", ubicacion)
        estado = _texto(conexion, "estado", ubicacion)
        if origen not in nodos or destino not in nodos:
            raise ValueError(f"{ubicacion}: origen o destino no existe en nodos")
        if estado not in ESTADOS:
            raise ValueError(f"{ubicacion}: estado debe ser uno de {', '.join(sorted(ESTADOS))}")
        fuente = _texto(conexion, "fuente", ubicacion, obligatorio=False)
        if estado in {"observado", "relatado"} and not fuente:
            raise ValueError(f"{ubicacion}: '{estado}' requiere identificar su fuente")
        conexiones.append({
            "origen": origen,
            "destino": destino,
            "estado": estado,
            "detalle": _texto(conexion, "detalle", ubicacion),
            "fuente": fuente,
            "verificacion_pendiente": _texto(conexion, "verificacion_pendiente", ubicacion, obligatorio=False),
        })
    return nodos, conexiones


def reconstruir(datos: Any, objetivo: str) -> dict[str, Any]:
    """Sigue conexiones entrantes una sola vez por nodo, incluso si hay ciclos."""
    nodos, conexiones = validar(datos)
    if objetivo not in nodos:
        raise ValueError(f"El objetivo '{objetivo}' no existe en nodos")

    entrantes: dict[str, list[dict[str, str]]] = {nodo: [] for nodo in nodos}
    for conexion in conexiones:
        entrantes[conexion["destino"]].append(conexion)

    cola = deque([objetivo])
    visitados = {objetivo}
    recorrido: list[dict[str, str]] = []
    while cola:
        destino = cola.popleft()
        for conexion in entrantes[destino]:
            recorrido.append(conexion)
            origen = conexion["origen"]
            if origen not in visitados:
                visitados.add(origen)
                cola.append(origen)

    return {
        "advertencia": ADVERTENCIA,
        "objetivo": nodos[objetivo],
        "nodos_alcanzados": [nodo for identificador, nodo in nodos.items() if identificador in visitados],
        "conexiones": recorrido,
    }


def _celda(valor: str) -> str:
    # Evita que los datos del usuario alteren las columnas de la tabla Markdown.
    return valor.replace("\\", "\\\\").replace("|", "\\|").replace("\r\n", " ").replace("\n", " ").replace("\r", " ")


def a_markdown(resultado: dict[str, Any]) -> str:
    objetivo = resultado["objetivo"]
    lineas = [
        f"# Reconstrucción inversa: {_celda(objetivo['descripcion'])}",
        "",
        resultado["advertencia"],
        "",
        "| Origen → destino | Clasificación | Lo declarado | Fuente | Verificación pendiente |",
        "|---|---|---|---|---|",
    ]
    for conexion in resultado["conexiones"]:
        celdas = [
            f"{conexion['origen']} → {conexion['destino']}",
            conexion["estado"],
            conexion["detalle"],
            conexion["fuente"] or "No indicada",
            conexion["verificacion_pendiente"] or "No especificada",
        ]
        lineas.append("| " + " | ".join(_celda(celda) for celda in celdas) + " |")
    if not resultado["conexiones"]:
        lineas.extend(["", "No hay conexiones entrantes declaradas para este objetivo; esto no prueba su inexistencia."])
    return "\n".join(lineas) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entrada", type=Path, help="JSON local con nodos y conexiones declaradas")
    parser.add_argument("--objetivo", required=True, help="ID del nodo desde el que reconstruir hacia atrás")
    parser.add_argument("--formato", choices=("md", "json"), default="md")
    args = parser.parse_args(argv)
    try:
        with args.entrada.open(encoding="utf-8") as archivo:
            datos = json.load(archivo)
        resultado = reconstruir(datos, args.objetivo)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    if args.formato == "json":
        print(json.dumps(resultado, ensure_ascii=False, indent=2))
    else:
        print(a_markdown(resultado), end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
