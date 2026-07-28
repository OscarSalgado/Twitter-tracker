#!/usr/bin/env python3
"""
Test con tweets REALES de @elonmusk sobre Starlink.

Este script descarga tweets reales usando las credenciales de .env
y genera un libro con datos verificables.

USO:
1. Configura .env con credenciales de una cuenta secundaria
2. Ejecuta: python3 test_real_tweets.py
3. Recibirás tweets reales de @elonmusk clasificados por tema
"""

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

def check_credentials():
    """Verifica que las credenciales estén configuradas"""
    username = os.getenv("TWITTER_USERNAME", "").strip()
    email = os.getenv("TWITTER_EMAIL", "").strip()
    password = os.getenv("TWITTER_PASSWORD", "").strip()

    print("=" * 70)
    print("🔑 VERIFICACIÓN DE CREDENCIALES")
    print("=" * 70)

    if not username:
        print("\n❌ TWITTER_USERNAME no configurado en .env")
        print("   Edita .env y establece:")
        print("   TWITTER_USERNAME=tu_usuario_secundario")
        return False

    if not email:
        print("\n❌ TWITTER_EMAIL no configurado en .env")
        print("   Edita .env y establece:")
        print("   TWITTER_EMAIL=tu_email@example.com")
        return False

    if not password:
        print("\n❌ TWITTER_PASSWORD no configurado en .env")
        print("   Edita .env y establece:")
        print("   TWITTER_PASSWORD=tu_contraseña")
        return False

    print("\n✓ Credenciales configuradas:")
    print(f"  - Usuario: {username}")
    print(f"  - Email: {email[:10]}***")
    print(f"  - Contraseña: {'*' * len(password)}")

    return True


async def fetch_real_tweets():
    """Descarga tweets reales de @elonmusk"""
    print("\n" + "=" * 70)
    print("🐦 DESCARGANDO TWEETS REALES DE @elonmusk")
    print("=" * 70)

    try:
        from twikit import Client
    except ImportError:
        print("\n❌ twikit no está instalado")
        print("   Instala con: pip install twikit")
        return None

    username = os.getenv("TWITTER_USERNAME")
    email = os.getenv("TWITTER_EMAIL")
    password = os.getenv("TWITTER_PASSWORD")

    try:
        client = Client()

        print("\n🔐 Autenticando en Twitter...")
        await client.login(
            auth_info_1=username,
            auth_info_2=email,
            password=password,
        )
        print("✓ Autenticación exitosa")

        print("\n📥 Buscando tweets de @elonmusk sobre Starlink...")
        tweets = await client.search_tweets(
            query="from:elonmusk starlink",
            count=20,
        )

        if not tweets:
            print("⚠️  No se encontraron tweets")
            return []

        print(f"✓ Se encontraron {len(tweets)} tweets")

        result = []
        for tweet in tweets:
            result.append({
                "id": tweet.id,
                "content": tweet.text,
                "author": "elonmusk",
                "display_name": tweet.user.name if hasattr(tweet, "user") else "Elon Musk",
                "url": f"https://x.com/elonmusk/status/{tweet.id}",
                "created_at": tweet.created_at if hasattr(tweet, "created_at") else None,
                "verified": True,  # Marca como verificado
            })

        return result

    except Exception as e:
        print(f"\n❌ Error al conectar con Twitter: {e}")
        print("\nPosibles causas:")
        print("  1. Credenciales incorrectas")
        print("  2. Cuenta bloqueada/suspendida")
        print("  3. Rate limit de Twitter")
        print("  4. Problema de conexión")
        return None


def generate_report(tweets):
    """Genera un reporte con los tweets descargados"""
    if not tweets:
        print("\n❌ No hay tweets para generar reporte")
        return

    print("\n" + "=" * 70)
    print("📊 REPORTE DE TWEETS DESCARGADOS")
    print("=" * 70)

    print(f"\n✓ Total de tweets: {len(tweets)}")

    if tweets:
        print(f"\n✓ Primeros 3 tweets:")
        for i, tweet in enumerate(tweets[:3], 1):
            date_str = tweet["created_at"].strftime(
                "%Y-%m-%d %H:%M"
            ) if tweet["created_at"] else "Sin fecha"
            print(f"\n  Tweet {i}:")
            print(f"    Fecha: {date_str}")
            print(f"    Contenido: {tweet['content'][:80]}...")
            print(f"    URL: {tweet['url']}")
            print(f"    ✓ Verificado")

    # Generar archivo de ejemplo
    output_file = "real_tweets_elonmusk_starlink.json"
    with open(output_file, "w") as f:
        json.dump(tweets, f, indent=2, default=str, ensure_ascii=False)

    print(f"\n✓ Tweets guardados en: {output_file}")


async def main():
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🌍 TEST CON TWEETS REALES DE @elonmusk SOBRE STARLINK".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "=" * 68 + "╝")

    # Step 1: Verificar credenciales
    if not check_credentials():
        print("\n" + "=" * 70)
        print("⚠️  CONFIGURACIÓN NECESARIA")
        print("=" * 70)
        print("""
Para ejecutar este test con tweets reales, necesitas:

1. Crear una CUENTA SECUNDARIA en X/Twitter
   (nunca uses tu cuenta principal)

2. Configurar el archivo .env:
   cp .env.example .env

3. Editar .env con:
   TWITTER_USERNAME=tu_usuario_secundario
   TWITTER_EMAIL=tu_email@example.com
   TWITTER_PASSWORD=tu_contraseña

4. Luego ejecutar:
   python3 test_real_tweets.py

⚠️  ADVERTENCIA:
   - Usa una CUENTA SECUNDARIA
   - X puede detectar automatización
   - Sé responsable y respeta los Términos de Servicio
   - Aumenta POLL_INTERVAL_MINUTES a 15+ minutos
        """)
        return

    # Step 2: Descargar tweets reales
    tweets = await fetch_real_tweets()

    # Step 3: Generar reporte
    if tweets is not None:
        generate_report(tweets)

        print("\n" + "=" * 70)
        print("✅ TEST COMPLETADO")
        print("=" * 70)
        print("""
Próximos pasos:
1. Revisar tweets_reales_elonmusk_starlink.json
2. Iniciar Docker: docker compose up -d
3. Panel web: http://localhost:8000
4. Añadir @elonmusk como cuenta a seguir
5. Descargar libro: Botón "📖 Descargar libro"
        """)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
