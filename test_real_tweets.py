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

def check_environment():
    """Verifica que el ambiente esté configurado"""
    print("=" * 70)
    print("🔧 VERIFICACIÓN DE AMBIENTE")
    print("=" * 70)

    print("\n✓ scweet NO requiere credenciales")
    print("  (scraping público de Twitter sin login)")

    try:
        from scweet import scrap
        print("\n✓ scweet está instalado")
    except ImportError:
        print("\n❌ scweet no está instalado")
        print("   Instala con: pip install scweet")
        return False

    try:
        import selenium
        print("✓ selenium está instalado")
    except ImportError:
        print("\n⚠️  selenium no está instalado")
        print("   Instala con: pip install selenium")
        print("   (requerido para scweet)")
        return False

    try:
        import pandas
        print("✓ pandas está instalado")
    except ImportError:
        print("\n⚠️  pandas no está instalado")
        print("   Instala con: pip install pandas")
        return False

    print("\n✓ Ambiente verificado correctamente")
    return True


async def fetch_real_tweets():
    """Descarga tweets reales de @elonmusk usando scweet"""
    print("\n" + "=" * 70)
    print("🐦 DESCARGANDO TWEETS REALES DE @elonmusk")
    print("=" * 70)

    try:
        from scweet import scrap
    except ImportError:
        print("\n❌ scweet no está instalado")
        print("   Instala con: pip install scweet")
        return None

    try:
        print("\n📥 Buscando tweets de @elonmusk sobre Starlink...")
        print("   (esto puede tomar 1-2 minutos)")

        # scweet scrapes sin necesidad de login
        tweets_df = scrap(
            username="elonmusk",
            tweets_count=20,
            save_images=False,
            resume=False,
        )

        if tweets_df is None or tweets_df.empty:
            print("⚠️  No se encontraron tweets")
            return []

        print(f"✓ Se encontraron {len(tweets_df)} tweets")

        result = []
        for _, row in tweets_df.iterrows():
            # Filtrar solo tweets sobre Starlink
            text = str(row.get("text", "")).lower()
            if "starlink" not in text and "satellite" not in text:
                continue

            result.append({
                "id": str(row.get("tweet_id", row.get("id", ""))),
                "content": str(row.get("text", "")),
                "author": "elonmusk",
                "display_name": "Elon Musk",
                "url": f"https://x.com/elonmusk/status/{row.get('tweet_id', row.get('id', ''))}",
                "created_at": row.get("created_at"),
                "verified": True,
            })

        print(f"✓ {len(result)} tweets sobre Starlink encontrados")
        return result

    except Exception as e:
        print(f"\n❌ Error al descargar tweets: {e}")
        print("\nPosibles causas:")
        print("  1. X/Twitter está bloqueando el scraping (temporal)")
        print("  2. Problema de conexión a Internet")
        print("  3. Selenium/WebDriver no configurado correctamente")
        print("  4. Problema con scweet o dependencias")
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

    # Step 1: Verificar ambiente
    if not check_environment():
        print("\n" + "=" * 70)
        print("⚠️  INSTALACIÓN NECESARIA")
        print("=" * 70)
        print("""
Para ejecutar este test con tweets reales, necesitas instalar:

1. Instalar dependencias:
   pip install scweet selenium pandas

2. Ejecutar:
   python3 test_real_tweets.py

✅ VENTAJAS DE SCWEET:
   - NO requiere credenciales de Twitter
   - Scraping público (sin login)
   - Simula un navegador real
   - Funciona con tweets públicos

⚠️  NOTAS:
   - El primer run puede tomar 1-2 minutos
   - X/Twitter puede bloquear scraping temporalmente
   - Usa esto responsablemente y respeta ToS
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
1. Revisar real_tweets_elonmusk_starlink.json
2. Iniciar Docker: docker compose up -d
3. Panel web: http://localhost:8000
4. Añadir @elonmusk como cuenta a seguir
5. Descargar libro: Botón "📖 Descargar libro"

El sistema ahora usa scweet para scraping:
✓ Sin credenciales necesarias
✓ Sin login requerido
✓ Tweets públicos accesibles
        """)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
