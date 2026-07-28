# Quick Start - Generador de Libros de Tweets

## 🚀 5 minutos para empezar

### 1. Configurar el proyecto

```bash
# Clonar o actualizar
git pull origin claude/tweet-collection-followed-accounts-hmrbop

# Copiar el archivo de configuración
cp .env.example .env

# Editar .env con tus credenciales
# TWITTER_USERNAME=tu_usuario
# TWITTER_EMAIL=tu_email
# TWITTER_PASSWORD=tu_contraseña
# BASIC_AUTH_PASSWORD=tu_contraseña_panel
```

### 2. Iniciar con Docker

```bash
# Construir e iniciar
docker compose up -d --build

# Acceder al panel
# http://localhost:8000
# Usuario: admin
# Contraseña: (la de BASIC_AUTH_PASSWORD)
```

### 3. Añadir cuentas para seguir

En el panel web:
1. Escribe el nombre de usuario (sin @)
2. Haz clic en "Seguir"
3. Espera el primer sondeo o haz clic en "Comprobar ahora"

### 4. Descargar tu libro

1. Haz clic en **📖 Descargar libro**
2. Se descargará un archivo `tweets_book.md`
3. Abre en tu editor favorito (VS Code, Obsidian, Notion, etc.)

## 📚 Ejemplos de uso

### Convertir a PDF

```bash
# Instalar pandoc (si no lo tienes)
sudo apt install pandoc

# Convertir
pandoc tweets_book.md -o tweets_book.pdf
```

### Convertir a HTML

```bash
pandoc tweets_book.md -o tweets_book.html
```

### Convertir a Word

```bash
pandoc tweets_book.md -o tweets_book.docx
```

## 🎨 Personalizar temas

Edita `app/themes.json`:

```json
{
  "themes": [
    {
      "name": "Mi Tema",
      "keywords": ["palabra1", "palabra2", "palabra3"]
    }
  ]
}
```

Luego reinicia la aplicación:
```bash
docker compose restart
```

## 📊 Estructura del libro

```
# Recopilación de Tweets

## Resumen
- Total de tweets: X
- Total de cuentas: Y
- Temáticas: Z

## [Tema 1]
- Tweet 1
- Tweet 2
...

## [Tema 2]
...
```

## ⚙️ Configuración avanzada

### Cambiar intervalo de sondeo

Edita `.env`:
```
POLL_INTERVAL_MINUTES=15
```

Valores recomendados:
- 5 min: Rastreo agresivo (más riesgo de bloqueo)
- 15 min: Balance recomendado
- 30+ min: Muy conservador

### Usar API REST

```bash
# Ver temas actuales
curl -u admin:password http://localhost:8000/book/themes | jq

# Descargar libro
curl -u admin:password http://localhost:8000/book/download > libro.md

# Actualizar temas
curl -X POST -u admin:password \
  -H "Content-Type: application/json" \
  -d @themes.json \
  http://localhost:8000/book/themes
```

## 🔍 Solucionar problemas

### "No se puede conectar a Twitter"
- Verifica credenciales en `.env`
- Usa una cuenta secundaria (X puede bloquear bots en cuenta principal)
- Espera 1 minuto antes de reintentar

### "Libro está vacío"
- Espera a que termine el primer sondeo
- Haz clic en "Comprobar ahora"
- Verifica que las cuentas están configuradas

### "Tweets no se clasifican"
- Revisa keywords en `app/themes.json`
- Las keywords son case-insensitive
- Añade más palabras clave si es necesario

## 📱 Validación sandbox

Para probar sin credenciales reales:

```bash
python3 test_starlink_simple.py
```

Esto genera un archivo de prueba con tweets simulados sobre Starlink.

## ✅ Checklist de uso

- [ ] `.env` configurado con credenciales
- [ ] Docker iniciado
- [ ] Panel accesible en http://localhost:8000
- [ ] Cuentas añadidas para seguir
- [ ] Primer sondeo completado
- [ ] Libro descargado correctamente
- [ ] Temas personalizados (opcional)

## 💡 Tips

1. **Guarda regularmente**: Descarga el libro periodicamente como backup
2. **Busca en markdown**: Usa `grep -n "palabra" tweets_book.md`
3. **Edita sin miedo**: El markdown es editable y no afecta el original
4. **Versionea**: Commit de libros generados en Git para histórico
5. **Automatiza**: Usa cron para descargar automáticamente

## 📞 Soporte

- Ver documentación completa: `BOOK_GENERATOR.md`
- Tests disponibles: `test_starlink_simple.py`
- Código fuente: `app/book_generator.py`

---

**Status**: ✅ Listo para producción | **Costo**: 🆓 Gratuito | **Mantención**: 0️⃣ Cero configuraciónc
