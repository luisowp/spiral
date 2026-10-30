---
name: redaccion-vincular-interamericana
description: Organiza la redacción en la voz de la persona usuaria, con fuentes, límites y separación entre vías. No sustituye revisión jurídica.
version: "1.2"
triggers: ["teoría del caso", "redacción", "autenticidad del expediente", "Fornerón", "CIDH"]
requires_context: ["fecha_corte", "fuentes", "hechos", "vía", "estado_procesal"]
related_skills: ["analizador-acuerdos", "scjn-bridge", "protocolo-revision-documentos"]
---

# Redacción vincular e interamericana

## Finalidad

Ayuda a la persona usuaria a expresar en su propia voz qué solicitó, a quién, qué respuesta recibió y qué efectos materiales refiere. Conserva sus tesis en primera persona sin transformarlas automáticamente en hechos probados ni diluirlas en un problema meramente registral. Pregunta por el objetivo y la vía, y mantén al día el contexto privado y el corte temporal.

Esta skill se activa explícitamente. El `analizador-acuerdos` permanece independiente: sus herramientas sirven para normas y trazabilidad instrumental, no para resolver el fondo familiar. Si se solicitan ambos temas, separa sus preguntas, fuentes y conclusiones.

## Prioridad material y medidas urgentes

Cuando se alegue una situación urgente que afecte a niños o adolescentes, conserva los datos que la persona identifique como constantes, atribuye los relatos y actualiza cambios. Examina la protección **individual** y la utilidad de cada medida solicitada; no presupongas desaparición, riesgos, ausencia de contacto ni una orden de convivencia.

Usa la secuencia **solicitud → recepción → decisión → notificación → ejecución → efecto**. Un plazo que se solicitó a otra persona no equivale a un plazo judicial concedido ni a un plazo legal; el tiempo transcurrido por sí solo no demuestra la violación. Verifica norma, vigencia, cómputo, actuaciones, respuestas previas y cumplimiento.

## Autenticidad y continuidad del expediente

Si la persona sostiene que un expediente exhibido es falso o que los folios no contienen sus promociones, conserva esa tesis de forma expresa y respetuosa. Contrasta por separado el escrito, acuse, folio o asiento, contenido accesible, objeto, resolución y notificación. Considera pruebas a favor y en contra; no presupongas falsificación, suplantación, intención, nulidad total ni autenticidad por la sola existencia de una copia.

## Audiencia y suplencia

Distingue la oportunidad efectiva de ser oído, los escritos, la asistencia personal, las actas y las resoluciones. Una objeción por escrito no equivale por sí sola a una audiencia, ni demuestra que fue examinada. Una copia que refiere una audiencia tampoco resuelve, por sí sola, una objeción de autenticidad o de notificación. Analiza la suplencia y su fundamento sin convertirla en una ampliación formal automática.

## Flujo de trabajo

1. Leer solo las piezas aportadas para el tramo actual y localizar página o párrafo. Antes de buscar fuentes adicionales, respetar la instrucción de la persona sobre consulta y disponibilidad de sus documentos.
2. Separar **documento**, **relato**, **hipótesis** y **pendiente**, con sus fuentes y límites. «No consta» en una pieza no significa que el hecho no ocurrió o que no exista evidencia en otra.
3. Aislar cada vía: familiar, amparo, penal, petición individual ante la CIDH y cautelares ante la CIDH tienen objetos y requisitos distintos. No prometer resultados ni saltarse el análisis de competencia, recursos o riesgos.
4. Cotejar fuentes jurídicas oficiales, vigencia, hechos y contexto del precedente. Distinguir jurisprudencia, tesis aislada, protocolo, sentencia internacional y resolución cautelar.
5. Elaborar solicitudes concretas, proporcionadas y verificables, con cautelas de privacidad y seguridad. Antes de presentar o enviar algo, comprobar documentos, actuaciones, plazos, destinatario y autorización de la persona.

Cuando la persona autorice el uso de un contexto privado, conserva sus constantes, fuentes y límites desde la ruta local que haya indicado; no sustituyas ese contexto por la plantilla ficticia pública. El ensamblador local `redactor.py` usa datos declarados en un JSON y genera un borrador por vía. No consulta sistemas ni autentica fuentes. El ejemplo público es ficticio; el material real debe mantenerse fuera de Git. Véanse [PRECEDENTES.md](PRECEDENTES.md), [README.md](README.md) y el esquema `../_schemas/redaccion-vincular.json`.
