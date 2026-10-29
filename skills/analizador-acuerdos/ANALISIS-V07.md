# Análisis base — AG 12/2020 V07 (independiente)

> Fuente: 2020-12-0-AC_V07.html (1.2MB) → clean.utf8.txt 222k chars
> Versión con REFORMAS 28/10/2022 ya integradas (ADICIONADO/REFORMADO)

## Estructura real detectada (para que la skill no invente)
- CAPÍTULO PRIMERO Disposiciones Generales — Art 1 (objeto: expediente electrónico + videoconferencias), Art 2 (definiciones I a ... XVI, con reformas), Art 3 (bases integración cronológica)
- CAPÍTULO SEGUNDO Del Sistema Electrónico del PJF — Art 4-8
- CAPÍTULO TERCERO De los servicios electrónicos — Art 9-17
- ... (9 páginas, 34k palabras, 442 párrafos)

## Lo relevante para tu objetivo 1 (skill que quede para diversos acuerdos)
Art 1 y Art 3 son el núcleo que pedías:
- **Art 1:** regula promoción, trámite, consulta, resolución y notificación por vía electrónica
- **Art 3:** bases — firma electrónica, integración cronológica, distinguir digitalizado vs generado electrónicamente, coincidencia físico vs electrónico

Cada vez que un acuerdo cite "en términos del art. 3" o "art. 30/31 Ley de Amparo" la skill debe:
1. Extraer cita textual
2. Integrar lo ADICIONADO/REFORMADO (28/10/2022) en lectura clara
3. Conectar link al art. x/y exacto

## Lo relevante para tu objetivo 2 (partir del resultado, flujo en segundo plano)
Estado actual: NEUN 000000 (sin control) / 41504452 sobrepuesto / 38654211 outlier — documentado en neunarena.md

En segundo plano, el flujo que la skill debe generar automáticamente sin que lo pidas:
```
Resultado (000000) 
  ← falta de acto de creación NEUN vinculado a P7M fuente 13 abril (folio 12341272/2026)
  ← objeto renombrado 0265|0000|41504452|...|6660 (registro SISE, no NEUN)
  ← incumplimiento bases Art 3: no hay integración cronológica ni coincidencia fedatario verificable
```

Esto queda como plantilla JSON en _schemas/analisis-acuerdo.json — un acuerdo a la vez.

## Validación
Archivo V07 conservado íntegro en corpus/ para prueba real de la skill.
