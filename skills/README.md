# Skills y utilidades

Los archivos públicos contienen herramientas y ejemplos ficticios, no datos de expedientes reales. Actualiza la etapa, las fuentes y el régimen aplicable antes de emplear cualquiera de las skills.

## Analizador independiente de acuerdos

[SKILL.md](analizador-acuerdos/SKILL.md) explica el método; [ANALISIS-V07.md](analizador-acuerdos/ANALISIS-V07.md) presenta la base normativa del AG 12/2020. El analizador no incorpora el fondo familiar a la controversia sobre un acuerdo.

```sh
python skills/analizador-acuerdos/trazabilidad.py \
  skills/analizador-acuerdos/ejemplo-trazabilidad-sintetico.json --objetivo permiso
python skills/analizador-acuerdos/nomenclatura.py --referencia 12345678 \
  12340000876543210001110002220003.pdf
python -m unittest discover -s skills/analizador-acuerdos/tests -v
```

El recorrido sigue **conexiones declaradas**, con su estado y fuente; no las descubre ni autentica. La comparación de nombres solo corta posiciones, sin asignarles un significado oficial. `cotejar_imagenes.py` requiere PyMuPDF y compara recursos extraídos, no la autenticidad ni la identidad íntegra de un PDF o P7M.

## Redacción vincular

[SKILL.md](redaccion-vincular/SKILL.md) conserva la voz y las tesis de la persona usuaria, con una separación clara de hechos, relatos, hipótesis y pendientes. [PRECEDENTES.md](redaccion-vincular/PRECEDENTES.md) ofrece fuentes jurídicas generales y sus límites.

```sh
python skills/redaccion-vincular/redactor.py \
  skills/redaccion-vincular/ejemplo-sintetico.json --via familiar
python -m unittest discover -s skills/redaccion-vincular/tests -v
```

Las vías disponibles son `familiar`, `amparo`, `penal`, `peticion-cidh` y `cautelares-cidh`. El ensamblador valida forma y referencias cruzadas, pero no hechos, firmas, plazos ni procedencia jurídica. La salida es un borrador que exige revisión humana. El esquema de entrada está en `_schemas/redaccion-vincular.json`.

## Contexto privado

`_context/caso.json` y `caso.yaml` son plantillas ficticias. El contexto real puede suministrarse desde una ruta local excluida de Git; no pongas datos reales, documentos o enlaces privados en el repositorio público. `local-confidencial/` está ignorado, pero no cifrado. Comprueba siempre las fuentes y solicita autorización antes de compartir información.
