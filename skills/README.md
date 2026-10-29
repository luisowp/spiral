# Skills — centro y periferia

**Centro:** tu intención (qué quieres lograr con el litigio).
**Periferia:** GitHub guarda la memoria.

## Estructura v2 (después de depuración 29 oct)

- `scjn-v2/openai.yaml` → YAML=configuración declarativa (cuándo se activa la skill)
- `scjn-v2/SKILL.md` → markdown=legible para humano y para ChatGPT (rol + equipo 3 expertos + reglas)
- `_schemas/*.json` → JSON=intercambio estructurado (salida verificable para máquina)
- `_context/caso.json|yaml` → fuente única de verdad (no hardcodear 5 vs 7 meses en el prompt)
- `protocolo-revision/SKILL.md` → tratamiento especial, transversal (legal y no legal)
- `validador.py` → Python=ejecución/validador (verifica que JSON cumpla schema y que no haya hechos sin fuente)

## Qué se depuró
- Duplicación MODO vs SKILL → unificado
- Hardcodeo contradictorio → parametrizado
- Instrucción peligrosa "las sentencias existen" → protocolo anti-alucinación (si no hay acceso CJF, declara pendiente verificación)
- allow_implicit_invocation true → false (activación explícita en tema sensible)

## Acotación 29 oct noche — Tema 3

**Foco independiente:** `analizador-acuerdos/` — base Acuerdo General 12/2020

- `analizador-acuerdos/SKILL.md` → analiza un acuerdo a la vez, integra adiciones, conecta "en términos del art. x" con link
- `analizador-acuerdos/agents/openai.yaml` → YAML declarativo (no mezcla con LGDNNA/protocolo infancia)
- `analizador-acuerdos/assets/icon.svg` → cara de la skill
- `_schemas/analisis-acuerdo.json` → JSON con lectura clara + integración + conexión caso + flujo segundo plano

Objetivo 1: skill que quede para diversos acuerdos (especializada, no genérica).
Objetivo 2: partir del resultado (neunarena.md: 000000 / 41504452 / 38654211) y desarrollar flujo automáticamente en segundo plano.

## Uso en ChatGPT
1. Sube `scjn-v2/SKILL.md` como skill (puente SCJN).
2. Sube `analizador-acuerdos/SKILL.md` como skill independiente (riel 12/2020).
3. Al iniciar chat, pega el contenido de `_context/caso.json`.
4. Si subes documento, se activa automáticamente `protocolo-revision`.
