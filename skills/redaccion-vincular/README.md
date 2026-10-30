# Uso de redacción vincular

Este directorio contiene una herramienta local para organizar información declarada por vía. El archivo `ejemplo-sintetico.json` es ficticio y no describe ningún caso real.

```sh
python skills/redaccion-vincular/redactor.py \
  skills/redaccion-vincular/ejemplo-sintetico.json --via familiar
```

Sustituye `familiar` por `amparo`, `penal`, `peticion-cidh` o `cautelares-cidh` para generar otra sección. El archivo de entrada debe respetar `_schemas/redaccion-vincular.json`: fuentes, hechos, criterios y bloques tienen identificadores y referencias cruzadas. El programa valida estructura, fechas y referencias; **no verifica la verdad de los hechos ni la procedencia legal**.

Para trabajar con información privada, utiliza un JSON local que no esté en Git, por ejemplo bajo `local-confidencial/`. Esa carpeta está ignorada, no cifrada. Si conservas una copia local previa en `local-confidencial/original/skills/redaccion-vincular/caso-ejemplo.json`, puedes pasar esa ruta al programa en lugar del ejemplo público. No compartas el archivo de entrada ni el borrador sin revisar su contenido y destinatario. Mantén copias seguras fuera del repositorio.

```sh
python -m unittest discover -s skills/redaccion-vincular/tests -v
```

El borrador no es un escrito listo para presentar. Una persona competente debe verificar fuentes, autenticidad, vigencia, actuaciones, vía, plazos y riesgos antes de cualquier presentación.
