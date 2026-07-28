# Generador de Libros de Tweets

La funcionalidad de generador de libros te permite crear una recopilación en Markdown de todos los tweets que has recopilado, organizados automáticamente por temáticas.

## Características

- **Clasificación automática**: Los tweets se clasifican automáticamente en temas basándose en palabras clave
- **Markdown editable**: El resultado es un archivo Markdown limpio y fácil de editar
- **Temas personalizables**: Puedes añadir, modificar o eliminar temas y sus palabras clave
- **Interfaz web**: Descarga el libro directamente desde el panel web
- **API REST**: Endpoints para acceder y modificar configuración de temas

## Cómo usar

### Desde la web

1. Abre el panel de Twitter Tracker (`http://localhost:8000`)
2. Haz clic en el botón **📖 Descargar libro**
3. Se generará un archivo `tweets_book.md` con todos tus tweets organizados por tema

### Mediante API

#### Descargar el libro

```bash
curl -u usuario:contraseña http://localhost:8000/book/download > tweets_book.md
```

#### Ver configuración de temas

```bash
curl -u usuario:contraseña http://localhost:8000/book/themes | jq .
```

#### Actualizar temas

```bash
curl -X POST -u usuario:contraseña \
  -H "Content-Type: application/json" \
  -d @themes.json \
  http://localhost:8000/book/themes
```

## Configuración de Temas

Los temas se definen en `app/themes.json`. Cada tema tiene:

- `name`: Nombre de la temática (ej: "Tecnología")
- `keywords`: Lista de palabras clave para identificar tweets de este tema

### Ejemplo de configuración

```json
{
  "themes": [
    {
      "name": "Tecnología",
      "keywords": ["tech", "código", "software", "python", "javascript"]
    },
    {
      "name": "Negocios",
      "keywords": ["startup", "inversión", "mercado", "empresa"]
    }
  ]
}
```

### Cómo funciona la clasificación

1. Se toma el contenido de cada tweet y se convierte a minúsculas
2. Se buscan todas las palabras clave en el contenido
3. El tweet se clasifica en el primer tema cuya palabra clave aparezca
4. Si no coincide con ningún tema, se clasifica en "Sin clasificar"

**Nota**: La búsqueda de palabras clave es sensible al contexto pero insensible a mayúsculas. Por ejemplo:
- `"Python"` detectará "python", "PYTHON", "Python"
- `"code"` detectará "code" pero no "encoder"

### Mejores prácticas

1. **Usa palabras clave específicas**: `"python"` es mejor que `"p"`
2. **Evita conflictos**: Ordena por especificidad (palabras más específicas primero)
3. **Agrupa palabras relacionadas**: `["tech", "tecnología", "software"]` en el tema "Tecnología"
4. **Mantén actualizado**: Añade nuevas palabras clave regularmente para mejorar la clasificación

## Estructura del Libro Generado

El archivo Markdown contiene:

```
# Recopilación de Tweets

## Resumen
- Total de tweets: X
- Total de cuentas seguidas: Y
- Temáticas: Z

## [Nombre del Tema]

*N tweets*

**@usuario** (Nombre de Usuario)
_Publicado: 15/01/2024 10:30_

Contenido del tweet...

[Ver en Twitter](url)

---
```

## Características Avanzadas

### Buscar en el Markdown

Una vez descargado, puedes buscar en el archivo:

```bash
grep -n "palabra" tweets_book.md
```

### Convertir a otros formatos

**A PDF** (requiere `pandoc`):
```bash
pandoc tweets_book.md -o tweets_book.pdf
```

**A HTML**:
```bash
pandoc tweets_book.md -o tweets_book.html
```

**A Word** (requiere `pandoc`):
```bash
pandoc tweets_book.md -o tweets_book.docx
```

### Editar el libro

El Markdown es completamente editable. Puedes:
- Reorganizar secciones
- Añadir comentarios personales
- Remover tweets
- Cambiar el orden

## Limitaciones y Consideraciones

- Los tweets se clasifican **solo una vez** al generar el libro (no se actualizan si modificas los temas)
- La clasificación es **por coincidencia de palabras clave**, no por IA/ML
- Si un tweet contiene múltiples palabras clave, se asigna al primer tema coincidente
- Los tweets sin fecha se muestran con la fecha de recopilación

## Ejemplos de Uso

### Crear un libro de "solo Tecnología"

Descarga el archivo y abre en tu editor. Luego busca y elimina las secciones que no quieres:

```bash
# Ver todas las secciones
grep "^##" tweets_book.md

# Editar con nano
nano tweets_book.md
```

### Crear múltiples libros por tema

Modifica `app/themes.json` para crear diferentes configuraciones y descarga:

```json
{
  "themes": [
    {
      "name": "Mi Tema Actual",
      "keywords": ["palabra1", "palabra2"]
    }
  ]
}
```

### Automatizar generación

Usa `cron` para generar el libro automáticamente:

```bash
0 0 * * * curl -s -u usuario:pass http://localhost:8000/book/download > /backups/tweets_$(date +\%Y-\%m-\%d).md
```

## Troubleshooting

**P: El archivo es muy grande**
R: Esto es normal si tienes muchos tweets. Considera dividirlo o usar las herramientas de búsqueda de tu editor.

**P: Algunos tweets aparecen en "Sin clasificar"**
R: Añade más palabras clave en `app/themes.json` o sé menos específico con las palabras clave.

**P: Quiero cambiar los temas regularmente**
R: Edita `app/themes.json` directamente o usa el endpoint `POST /book/themes`.

**P: ¿Se puede filtrar por fecha?**
R: No directamente, pero puedes editar el Markdown manualmente o usar herramientas como `grep` con patrones de fecha.
