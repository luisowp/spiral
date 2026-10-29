# Skills — centro y periferia

**Centro:** tu intención (qué quieres lograr con el litigio).
**Periferia:** GitHub guarda la memoria.

## Estructura v2 (después de depuración)

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

## Uso en ChatGPT
1. Sube `scjn-v2/SKILL.md` como skill.
2. Al iniciar chat, pega el contenido de `_context/caso.json`.
3. Si subes documento, se activa automáticamente `protocolo-revision`.
