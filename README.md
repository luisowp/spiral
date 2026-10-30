# Spiral

Herramientas para examinar documentos, acuerdos y opciones de redacción jurídica con fuentes trazables y límites explícitos. El análisis instrumental de acuerdos se mantiene separado de la controversia de fondo.

## Componentes

- [Analizador de acuerdos](skills/analizador-acuerdos/SKILL.md): normativa aplicable, expediente electrónico, turno y trazabilidad de relaciones declaradas. Incluye una base sobre el Acuerdo General 12/2020 y utilidades locales de comparación.
- [Redacción vincular e interamericana](skills/redaccion-vincular/SKILL.md): organiza hechos, fuentes, criterios y solicitudes por vía sin convertir alegaciones en hechos probados.
- [Protocolo de revisión](skills/protocolo-revision/SKILL.md): extracción fiel, ubicación de las citas y distinción entre contenido, inferencia y datos no constatados.
- [SCJN Bridge](skills/scjn-v2/SKILL.md): examina opciones procesales solo si la competencia, la etapa y las fuentes pueden verificarse.

Los ejemplos incluidos son **ficticios**. Ninguna herramienta se conecta automáticamente a un expediente judicial, autentica firmas, verifica hechos o determina por sí sola la procedencia de una acción.

## Privacidad

El repositorio es público: no incluyas nombres de personas, datos de menores, números reales de expediente, archivos originales ni enlaces privados en ejemplos, pruebas, commits o solicitudes de extracción. Guarda materiales de trabajo sensibles fuera del control de versiones; `local-confidencial/` está ignorado por Git, pero **no está cifrado**. La exclusión de Git no sustituye permisos de acceso, copias de seguridad ni medidas de seguridad adecuadas.

Los datos que se hubieran publicado en versiones anteriores pueden seguir disponibles en el historial; eliminarlos requiere una revisión específica, no solo un nuevo commit.

## Pruebas

```sh
python -m unittest discover -s skills/analizador-acuerdos/tests -v
python -m unittest discover -s skills/redaccion-vincular/tests -v
```

El cotejo de imágenes PDF usa la dependencia opcional PyMuPDF; las demás herramientas emplean la biblioteca estándar de Python. Consulta [skills/README.md](skills/README.md) para ejemplos de ejecución y límites.
