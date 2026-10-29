---
name: protocolo-revision-documentos
description: Tratamiento especial para revisión de documentos (legales y no legales). Extracción fiel, distinción hecho vs inferencia, citación trazable y salida dual markdown+JSON.
version: "2.0"
triggers: ["revisa documento", "analiza PDF", "protocolo de revisión", "tratamiento especial"]
output_schema: "../_schemas/revision-documento.json"
---

# SKILL: Protocolo de Revisión — Tratamiento Especial

> Esta skill es transversal. Nació para documentos legales, pero aplica a cualquier documento donde el error cueste.

## Principio
**Primero transcribe lo que dice, luego interpreta lo que significa. Nunca al revés.**

## Fases (siempre en este orden)

### 1. Inventario
- Lista documentos recibidos: nombre, tipo (demanda, acuerdo, sentencia, anexo, oficio, otro), fecha, fojas/páginas.
- Si es escaneado ilegible, declara: "OCR parcial, riesgo de error en foja X".

### 2. Extracción fiel (markdown)
- Cita textual corta (máx 40 palabras por cita) con referencia: `p.3, párr.2` o `foja 12`.
- No parafrasees como si fuera cita.

### 3. Mapa de hechos vs inferencias
| # | Tipo | Contenido | Fuente | Confianza |
|---|------|-----------|--------|-----------|
| 1 | HECHO | ... | p.2 párr.1 | alta |
| 2 | [INFERENCIA] | ... | deducción de 1+3 | media - verificar |
| 3 | VACÍO | No consta notificación | — | — |

### 4. Hallazgos críticos
- Inconsistencias, omisiones, plazos, violaciones procesales, riesgos.
- Para cada hallazgo: fundamento tentativo + qué falta para confirmarlo.

### 5. Salida dual obligatoria
- **Humano:** markdown legible con semáforo: 🟢 hecho verificado / 🟡 por verificar / 🔴 inconsistencia.
- **Máquina:** JSON válido según `revision-documento.json` (para que Python u otro agente lo valide).

## Reglas especiales (tratamiento especial)
1. **No inventar norma:** si citas artículo/acuerdo, cita texto o di "no verificado en esta sesión".
2. **Menores y datos sensibles:** minimiza exposición. Usa iniciales si es posible.
3. **Voz del usuario:** respeta si habla como "Luis", "El Arquitecto" o "parte actora". No cambies identidad.
4. **No conclusión sin trazabilidad:** toda conclusión debe tener fila en tabla de hechos.

## Relación con formatos
- **markdown:** es tu acta de lectura (humano).
- **yaml:** configura qué revisar (ej: `enfasis: [plazos, notificaciones]`).
- **json:** es tu prueba de trabajo estructurada (máquina).
- **python:** es tu validador (verifica que JSON tenga citas y no haya hechos sin fuente).

## Ejemplo de invocación en ChatGPT
```
Aplica protocolo-revision-documentos con enfasis en: plazos y omisión.
Documento: [adjunta PDF]
Contexto: Amparo 334/2026-4A, Recurso de Queja
```
