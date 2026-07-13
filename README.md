# Twitter Tracker

Instancia **autoalojada, gratuita y de código abierto** para seguir y trackear
cuentas de Twitter/X: añade los usuarios que quieras vigilar y la aplicación
revisa periódicamente si han publicado tuits nuevos, los guarda en un
panel web y (opcionalmente) te avisa por Telegram.

No usa la API oficial de pago de X. En su lugar utiliza
[`twikit`](https://github.com/d60/twikit) (MIT), una librería open source que
inicia sesión como una cuenta normal para leer contenido público, igual que
haría un navegador.

## ⚠️ Aviso importante

- Usa una **cuenta secundaria** dedicada para esto, nunca tu cuenta personal
  principal: hay riesgo de bloqueo/suspensión si X detecta automatización.
- Respeta los [Términos de Servicio de X](https://x.com/tos) y las cuentas
  que sigas (usa esto para cuentas públicas y con fines legítimos: noticias,
  monitorización de tu propia marca, investigación, etc.).
- Ajusta `POLL_INTERVAL_MINUTES` a un valor razonable (15 minutos o más) para
  minimizar el riesgo de rate-limiting o bloqueos.
- Este proyecto se ofrece "tal cual", sin garantías; su funcionamiento puede
  romperse si X cambia su plataforma interna.

## Características

- Sigue un número ilimitado de cuentas públicas de Twitter/X.
- Sondeo automático en segundo plano cada N minutos (configurable).
- Panel web sencillo para añadir/eliminar cuentas y ver los tuits recopilados.
- Notificaciones opcionales por Telegram cuando aparece un tuit nuevo.
- Persistencia en SQLite (sin dependencias externas de base de datos).
- 100% Docker: una sola instancia, fácil de desplegar en cualquier VPS.
- Autenticación básica opcional para proteger el panel.

## Arquitectura

```
app/
  main.py            FastAPI: rutas del panel web y API mínima
  scraper.py          Wrapper sobre twikit (login, lectura de tuits)
  tracker_service.py  Lógica de añadir cuentas y sondear tuits nuevos
  scheduler.py         Tarea periódica (APScheduler)
  notifier.py          Notificaciones por Telegram
  models.py / database.py   Modelos SQLAlchemy + SQLite
  templates/, static/  Interfaz web (Jinja2 + CSS, sin frameworks JS)
```

## Puesta en marcha (Docker, recomendado)

1. Copia el archivo de configuración de ejemplo:

   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y rellena al menos:

   - `TWITTER_USERNAME`, `TWITTER_EMAIL`, `TWITTER_PASSWORD` — credenciales de
     la cuenta que usará la instancia para leer tuits.
   - `BASIC_AUTH_PASSWORD` — contraseña para proteger el panel web.
   - (Opcional) `TELEGRAM_BOT_TOKEN` y `TELEGRAM_CHAT_ID` para notificaciones.

3. Levanta la instancia:

   ```bash
   docker compose up -d --build
   ```

4. Abre `http://localhost:8000` e inicia sesión con `BASIC_AUTH_USER` /
   `BASIC_AUTH_PASSWORD`. Añade las cuentas que quieras seguir desde el
   formulario del panel.

Los datos (base de datos SQLite y cookies de sesión de Twitter) se guardan en
`./data`, que se persiste como volumen entre reinicios del contenedor.

## Puesta en marcha (sin Docker)

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # y edítalo
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Notificaciones por Telegram

1. Crea un bot con [@BotFather](https://t.me/BotFather) y copia el token en
   `TELEGRAM_BOT_TOKEN`.
2. Escríbele al bot (o añádelo a un grupo/canal) y obtén el `chat_id` — por
   ejemplo con `https://api.telegram.org/bot<token>/getUpdates`.
3. Rellena `TELEGRAM_CHAT_ID` en `.env` y reinicia la instancia.

## Desarrollo con OpenSpec

Este proyecto usa [OpenSpec](https://github.com/Fission-AI/OpenSpec) para
desarrollo dirigido por especificación: el comportamiento vigente de cada
capacidad vive como Markdown versionado en `openspec/specs/`, y todo cambio
de comportamiento se propone primero como spec antes de tocar código.

- `openspec/specs/` — especificación actual de cada capacidad
  (`account-tracking`, `tweet-polling`, `notifications`, `web-dashboard`).
- `openspec/changes/` — propuestas de cambio en curso (se archivan en
  `openspec/changes/archive/` una vez implementadas).
- `openspec/config.yaml` — contexto del proyecto y convenciones para la IA.

Para trabajar con OpenSpec necesitas la CLI (Node.js 20.19+):

```bash
npx @fission-ai/openspec@latest list --specs   # ver capacidades existentes
npx @fission-ai/openspec@latest validate --specs --strict
```

Con Claude Code, los comandos `/opsx:explore`, `/opsx:propose`, `/opsx:apply`
y `/opsx:archive` (instalados en `.claude/commands/opsx/`) guían el flujo:
explorar el problema → proponer spec + diseño + tareas → implementar →
archivar el cambio fusionando la spec delta en `openspec/specs/`.

## Licencia

MIT — ver [LICENSE](LICENSE).
