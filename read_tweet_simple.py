#!/usr/bin/env python3
"""
Lector simple de tweets usando requests + web scraping.
Alternativa a scweet cuando hay problemas de dependencias.
"""

import requests
import json
from datetime import datetime
import re

def fetch_tweet_via_api(username="elonmusk"):
    """
    Intenta obtener el tweet más reciente usando la API interna de X/Twitter
    (método usado por navegadores)
    """
    print(f"🔍 Buscando último tweet de @{username}...")
    print("   Conectando a Twitter...\n")

    try:
        # Usar el endpoint de la API interna de Twitter (guest token)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        }

        # URL del perfil de Twitter
        url = f"https://x.com/{username}"
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        # Buscar datos JSON embebidos en el HTML
        # Twitter embebe datos iniciales en el HTML como JSON
        match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">({.*?})</script>',
                         response.text, re.DOTALL)

        if match:
            data = json.loads(match.group(1))
            print("✓ Conectado a Twitter")
            return data
        else:
            print("⚠️  No se encontraron datos de tweets")
            return None

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def fetch_tweet_demo():
    """
    Demostración con datos de ejemplo cuando no hay acceso a la API
    """
    print("🔍 Buscando último tweet de @elonmusk...")
    print("   (Modo demostración - usando datos de ejemplo)\n")

    return {
        "author": "elonmusk",
        "display_name": "Elon Musk",
        "content": "Starlink is now providing global connectivity. Next generation satellites launching soon.",
        "tweet_id": "1824506789",
        "created_at": "2026-08-29T10:30:00Z",
        "url": "https://x.com/elonmusk/status/1824506789",
        "likes": 125430,
        "retweets": 45230,
        "replies": 8921,
        "mode": "demo"
    }


def display_tweet(tweet):
    """Muestra el tweet de forma formateada"""

    if tweet.get("mode") == "demo":
        print("═" * 78)
        print("⚠️  MODO DEMOSTRACIÓN (datos de ejemplo)")
        print("═" * 78)
        print()

    print("╔" + "=" * 76 + "╗")
    print("║" + " " * 76 + "║")
    print("║" + f"  🐦 ÚLTIMO TWEET DE @{tweet['author']}".ljust(76) + "║")
    print("║" + " " * 76 + "║")
    print("╚" + "=" * 76 + "╝\n")

    # Información del tweet
    print(f"👤 Autor: @{tweet['author']} ({tweet['display_name']})")
    print(f"📅 Fecha: {tweet['created_at']}")
    print(f"🔗 URL: {tweet['url']}")

    print("\n" + "─" * 78)
    print("\n📝 Contenido:\n")
    print(f"{tweet['content']}")
    print("\n" + "─" * 78)

    # Estadísticas
    print("\n📊 Estadísticas:")
    print(f"   ❤️  Likes: {tweet.get('likes', 0):,}")
    print(f"   🔄 Retweets: {tweet.get('retweets', 0):,}")
    print(f"   💬 Respuestas: {tweet.get('replies', 0):,}")

    print("\n" + "=" * 78 + "\n")


def main():
    print("\n")
    print("╔" + "=" * 76 + "╗")
    print("║" + " " * 76 + "║")
    print("║" + "  📖 LECTOR DE TWEETS - @elonmusk (Versión Simple)".ljust(76) + "║")
    print("║" + " " * 76 + "║")
    print("╚" + "=" * 76 + "╝\n")

    # Intentar obtener tweet real
    tweet = fetch_tweet_via_api("elonmusk")

    # Si falla, usar demostración
    if tweet is None:
        tweet = fetch_tweet_demo()

    if tweet:
        display_tweet(tweet)
        print("✅ Tweet cargado correctamente\n")
    else:
        print("❌ No se pudo cargar el tweet\n")


if __name__ == "__main__":
    main()
