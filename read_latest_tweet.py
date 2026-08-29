#!/usr/bin/env python3
"""
Script para descargar y mostrar el último tweet de @elonmusk
usando scweet (sin credenciales necesarias).
"""

import pandas as pd
from datetime import datetime

try:
    from scweet import scrap
except ImportError:
    print("❌ scweet no está instalado")
    print("   Instala con: pip install scweet selenium pandas")
    exit(1)


def get_latest_tweet(username="elonmusk", count=5):
    """Descarga los últimos tweets de un usuario"""
    print(f"🔍 Buscando últimos tweets de @{username}...")
    print("   (esto puede tomar 30-60 segundos)\n")

    try:
        # Descargar tweets
        tweets_df = scrap(
            username=username,
            tweets_count=count,
            save_images=False,
            resume=False,
        )

        if tweets_df is None or tweets_df.empty:
            print(f"❌ No se encontraron tweets de @{username}")
            return None

        # Ordenar por fecha (más reciente primero)
        if "created_at" in tweets_df.columns:
            tweets_df["created_at"] = pd.to_datetime(tweets_df["created_at"], errors="coerce")
            tweets_df = tweets_df.sort_values("created_at", ascending=False)

        # Obtener el primer tweet (más reciente)
        latest = tweets_df.iloc[0]

        return latest

    except Exception as e:
        print(f"❌ Error: {e}")
        return None


def display_tweet(tweet):
    """Muestra el tweet de forma legible"""
    print("╔" + "=" * 76 + "╗")
    print("║" + " " * 76 + "║")
    print("║" + "  🐦 ÚLTIMO TWEET DE @elonmusk".ljust(76) + "║")
    print("║" + " " * 76 + "║")
    print("╚" + "=" * 76 + "╝")

    # Extraer información
    author = "elonmusk"
    display_name = "Elon Musk"
    content = str(tweet.get("text", ""))
    tweet_id = str(tweet.get("tweet_id", tweet.get("id", "")))
    created_at = tweet.get("created_at", "")

    # Formatear fecha
    if created_at:
        try:
            if isinstance(created_at, str):
                dt = pd.to_datetime(created_at)
            else:
                dt = created_at
            fecha_str = dt.strftime("%d de %B de %Y a las %H:%M:%S UTC")
        except:
            fecha_str = str(created_at)
    else:
        fecha_str = "Fecha desconocida"

    # Mostrar información
    print(f"\n👤 Autor: @{author} ({display_name})")
    print(f"📅 Fecha: {fecha_str}")
    print(f"🔗 URL: https://x.com/{author}/status/{tweet_id}")
    print("\n" + "─" * 78)
    print("\n📝 Contenido:\n")
    print(content)
    print("\n" + "─" * 78)

    # Estadísticas si disponibles
    print("\n📊 Estadísticas:")
    likes = tweet.get("like_count", tweet.get("likes", 0))
    retweets = tweet.get("retweet_count", tweet.get("retweets", 0))
    replies = tweet.get("reply_count", tweet.get("replies", 0))

    if likes:
        print(f"   ❤️  Likes: {likes:,}")
    if retweets:
        print(f"   🔄 Retweets: {retweets:,}")
    if replies:
        print(f"   💬 Respuestas: {replies:,}")

    print("\n" + "=" * 78)


def main():
    print("\n")
    print("╔" + "=" * 76 + "╗")
    print("║" + " " * 76 + "║")
    print("║" + "  📖 LECTOR DE TWEETS - Último tweet de @elonmusk".ljust(76) + "║")
    print("║" + " " * 76 + "║")
    print("╚" + "=" * 76 + "╝")
    print()

    # Descargar tweet
    tweet = get_latest_tweet("elonmusk", count=1)

    if tweet is not None:
        display_tweet(tweet)
        print("\n✅ Tweet descargado correctamente\n")
    else:
        print("\n❌ No se pudo descargar el tweet\n")


if __name__ == "__main__":
    main()
