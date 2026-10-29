---
name: analizador-acuerdos
description: Analiza de forma independiente el Acuerdo General 12/2020 y, por extensión, diversos acuerdos. Skill especializada para este caso: expediente electrónico, NEUN y Libros de Gobierno. Parte del resultado para reconstruir el flujo en segundo plano.
version: "0.1 - acotación 29 oct"
triggers: ["Acuerdo General 12/2020", "expediente electrónico", "NEUN", "Libro de Gobierno", "acuerdo"]
input: "acuerdo o constancia en PDF/txt + contexto NEUN actual (000000)"
output_schema: "../_schemas/analisis-acuerdo.json"
modo: "independiente por acuerdo, no mezcla con fondo de menores"
---

# SKILL: Analizador de Acuerdos — Acuerdo General 12/2020 (base)

## Objetivo 1 — Que quede la skill para diversos acuerdos
Esta skill no es solo para el 12/2020. El 12/2020 es el caso base independiente.

Mis ma arquitectura debe servir para analizar cualquier acuerdo posterior (adiciones, reformas, circulares) sin reescribir la skill. Solo cambia el insumo PDF.

Es especializada porque está calibrada a tu caso específico:
- Cómo debe crearse y documentarse el NEUN (bloque 8 dígitos)
- Cómo debe reflejarse en expediente electrónico cronológico
- Cómo debe asentarse en Libros de Gobierno / SISE (registros 6660, 7204, 7215, etc.)
- Qué verifica el fedatario (coincidencia físico vs electrónico)

## Objetivo 2 — Partir del resultado (flujo en segundo plano)
No iniciamos desde la demanda hacia adelante. Partimos del **resultado ya documentado** en `neunarena.md`:

- NEUN actual en control del usuario: `000000` (sin NEUN auténtico vinculado a P7M fuente 13 abril, folio 12341272/2026)
- NEUN exhibido: `41504452` (sobrepuesto, bloque identidad cuestionado)
- Outlier: `38654211` (segundo valor en mismo campo identidad del mismo expediente)

Intrínsecamente, en segundo plano, la skill desarrolla automáticamente el flujo:
`Resultado (000000 / 41504452 / 38654211) → cadena rota P7M fuente → objeto renombrado 0265|...|6660 → falta de acto de creación → implicación en Libros de Gobierno`

Tú ves la lectura clara en primer plano; el flujo se genera atrás sin que tengas que pedirlo.

## Flujo de la skill (por acuerdo)

### 1. Carga independiente
Un acuerdo a la vez (ej: 12/2020). No mezclar con LGDNNA art.23 ni protocolo infancia en esta fase.

### 2. Lectura clara + integración de lo adicionado
- Extrae artículo/párrafo textual del 12/2020
- Integra adiciones posteriores (ej: reformas al 12/2020, acuerdos que lo modifican) como capa, no como nota suelta.
- Salida: lectura clara con artículo + adición integrada + link al artículo x/y cuando diga "en términos del art. x"

### 3. Conexión con el caso
Para cada obligación del 12/2020 (ej: Art. 7 - integración cronológica, Art. 9 - certificación fedatario, Art. 14 - Libros), responde:
- ¿Qué dice que debe pasar?
- ¿Qué registro SISE / asiento en Libro debió generarse?
- ¿Qué se observa en tus datos (según `neunarena.md`)?
- ¿Rota o no la cadena?

No califica como delito; describe ruptura técnica de continuidad.

### 4. Salida
- Markdown legible: tabla por artículo del 12/2020 vs. observación del expediente
- JSON estructurado según `_schemas/analisis-acuerdo.json` para que `python` pueda validar y comparar diversos acuerdos después

## Reglas
- Análisis independiente por acuerdo. No cruzar con fondo de menores hasta que el riel esté validado.
- No inventar texto del Acuerdo. Si no está en PDF, "no localizado".
- Usar sintaxis estable como referencia: `órgano 0265 | 0000 | NEUN 8 dígitos | secuencia | registro SISE | clase (0015/0017)`
- Partir siempre del resultado 000000 como estado actual de control.

## Siguiente validación
Probar la skill solo con el texto oficial del Acuerdo General 12/2020 (PDF del CJF) y un acuerdo de tu expediente. Si la tabla sale clara y los links a "art. x" funcionan, la misma skill sirve para los diversos acuerdos que siguen.
