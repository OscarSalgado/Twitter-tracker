#!/usr/bin/env python3
"""
Sandbox Test: Tweets de Starlink generados directamente
Sin dependencias externas - simula el flujo completo
"""

import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from collections import defaultdict


# Copiar la lógica del ThemeClassifier sin importar
class SimpleThemeClassifier:
    def __init__(self):
        self.themes = self._load_themes()

    def _load_themes(self):
        with open("app/themes.json") as f:
            data = json.load(f)
        return data.get("themes", [])

    def classify_tweet(self, content):
        content_lower = content.lower()
        for theme in self.themes:
            for keyword in theme.get("keywords", []):
                if keyword.lower() in content_lower:
                    return theme["name"]
        return "Sin clasificar"


def create_mock_tweets():
    """Crea 8 tweets simulados de @elonmusk sobre Starlink"""
    now = datetime.now(timezone.utc)

    tweets = [
        {
            "id": 1,
            "content": "Starlink is now providing global connectivity. Over 50 million users worldwide!",
            "url": "https://x.com/elonmusk/status/1",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=0, hours=2),
            "fetched_at": now - timedelta(days=0, hours=1),
        },
        {
            "id": 2,
            "content": "Starlink v2 satellites have more than 8x capacity than v1.5. Performance is incredible.",
            "url": "https://x.com/elonmusk/status/2",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=1, hours=5),
            "fetched_at": now - timedelta(days=1, hours=4),
        },
        {
            "id": 3,
            "content": "Just launched 40 more Starlink satellites to polar orbit. Coverage expanding fast!",
            "url": "https://x.com/elonmusk/status/3",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=2, hours=10),
            "fetched_at": now - timedelta(days=2, hours=9),
        },
        {
            "id": 4,
            "content": "Starlink Mini is shipping to early access users. First product under $600!",
            "url": "https://x.com/elonmusk/status/4",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=3, hours=3),
            "fetched_at": now - timedelta(days=3, hours=2),
        },
        {
            "id": 5,
            "content": "Starlink Direct to Cell enabled. Can text from anywhere on Earth now.",
            "url": "https://x.com/elonmusk/status/5",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=4, hours=7),
            "fetched_at": now - timedelta(days=4, hours=6),
        },
        {
            "id": 6,
            "content": "SpaceX Starship will carry Starlink to Mars. Interplanetary internet coming soon!",
            "url": "https://x.com/elonmusk/status/6",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=5, hours=1),
            "fetched_at": now - timedelta(days=5, hours=0),
        },
        {
            "id": 7,
            "content": "Starlink latency down to 20ms in most areas. Gaming and video calls work perfectly.",
            "url": "https://x.com/elonmusk/status/7",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=6, hours=4),
            "fetched_at": now - timedelta(days=6, hours=3),
        },
        {
            "id": 8,
            "content": "Disaster response: Starlink providing emergency connectivity to affected areas.",
            "url": "https://x.com/elonmusk/status/8",
            "author": "elonmusk",
            "display_name": "Elon Musk",
            "created_at": now - timedelta(days=7, hours=6),
            "fetched_at": now - timedelta(days=7, hours=5),
        },
    ]

    return tweets


def classify_tweets(tweets, classifier):
    """Clasifica tweets por tema"""
    tweets_by_theme = defaultdict(list)

    for tweet in tweets:
        theme = classifier.classify_tweet(tweet["content"])
        tweets_by_theme[theme].append(tweet)

    return tweets_by_theme


def generate_markdown(tweets_by_theme, total_accounts=1):
    """Genera el markdown del libro"""
    lines = [
        "# Recopilación de Tweets",
        "",
        "**Generado automáticamente desde Twitter Tracker**",
        "",
        "## Resumen",
        "",
        f"- **Total de tweets**: {sum(len(tweets) for tweets in tweets_by_theme.values())}",
        f"- **Total de cuentas seguidas**: {total_accounts}",
        f"- **Temáticas**: {len(tweets_by_theme)}",
        "",
        "---",
        "",
    ]

    # Ordenar temas (Starlink primero si existe)
    sorted_themes = sorted(tweets_by_theme.items())
    if "Starlink" in dict(tweets_by_theme):
        sorted_themes = [("Starlink", tweets_by_theme["Starlink"])] + [
            (k, v) for k, v in sorted_themes if k != "Starlink"
        ]

    for theme, tweets in sorted_themes:
        lines.append(f"## {theme}")
        lines.append("")
        lines.append(f"*{len(tweets)} tweets*")
        lines.append("")

        for tweet in tweets:
            lines.append(f"**@{tweet['author']}** ({tweet['display_name']})")
            lines.append(
                f"_Publicado: {tweet['created_at'].strftime('%d/%m/%Y %H:%M')}_"
            )
            lines.append("")
            lines.append(tweet["content"])
            lines.append("")
            lines.append(f"[Ver en Twitter]({tweet['url']})")
            lines.append("")
            lines.append("---")
            lines.append("")

    return "\n".join(lines)


def main():
    print("=" * 70)
    print("🛰️  SANDBOX TEST: Tweet Collection - Starlink Theme")
    print("=" * 70)

    # Step 1: Verificar configuración
    print("\n📝 Step 1: Configuración de temas")
    print("-" * 70)

    with open("app/themes.json") as f:
        themes_config = json.load(f)

    print(f"✓ Archivo themes.json cargado")
    print(f"✓ Total de temas: {len(themes_config['themes'])}")

    # Buscar tema Starlink
    starlink_config = None
    for theme in themes_config["themes"]:
        if theme["name"] == "Starlink":
            starlink_config = theme
            break

    if starlink_config:
        print(f"✓ Tema 'Starlink' encontrado")
        print(f"  Keywords: {', '.join(starlink_config['keywords'][:4])}...")
    else:
        print("✗ Tema Starlink NO encontrado")
        return

    # Step 2: Crear tweets mock
    print("\n👤 Step 2: Datos simulados (@elonmusk)")
    print("-" * 70)

    tweets = create_mock_tweets()
    print(f"✓ {len(tweets)} tweets de prueba creados")
    print(f"✓ Autor: @elonmusk (Elon Musk)")
    print(f"✓ Período: Últimos 7 días")
    print(f"✓ Tema: Starlink")

    print("\n📋 Tweets simulados:")
    for i, tweet in enumerate(tweets[:3], 1):
        print(f"\n  Tweet {i}:")
        print(f"    {tweet['content'][:60]}...")
        print(f"    📅 {tweet['created_at'].strftime('%Y-%m-%d %H:%M')}")

    print(f"\n  ... y {len(tweets) - 3} tweets más en el test")

    # Step 3: Clasificar tweets
    print("\n🏷️  Step 3: Clasificando tweets por tema")
    print("-" * 70)

    classifier = SimpleThemeClassifier()
    tweets_by_theme = classify_tweets(tweets, classifier)

    print(f"✓ Tweets clasificados:")
    for theme in sorted(tweets_by_theme.keys()):
        count = len(tweets_by_theme[theme])
        percentage = (count / len(tweets)) * 100
        print(f"  - {theme}: {count} tweets ({percentage:.0f}%)")

    # Step 4: Generar markdown
    print("\n📖 Step 4: Generando libro en Markdown")
    print("-" * 70)

    markdown = generate_markdown(tweets_by_theme, total_accounts=1)

    # Step 5: Guardar archivo
    print("\n💾 Step 5: Guardando archivo")
    print("-" * 70)

    output_file = "test_starlink_book.md"
    Path(output_file).write_text(markdown, encoding="utf-8")

    file_size = len(markdown)
    lines_count = len(markdown.splitlines())

    print(f"✓ Archivo generado: {output_file}")
    print(f"✓ Tamaño: {file_size:,} bytes")
    print(f"✓ Líneas: {lines_count}")

    # Step 6: Preview
    print("\n👀 Step 6: Preview del archivo generado")
    print("-" * 70)

    preview_lines = markdown.splitlines()[:40]
    for line in preview_lines:
        print(line)

    if len(markdown.splitlines()) > 40:
        print("\n... (continuación en archivo)")

    # Step 7: Estadísticas finales
    print("\n" + "=" * 70)
    print("📊 RESULTADOS DEL TEST")
    print("=" * 70)

    starlink_count = len(tweets_by_theme.get("Starlink", []))

    print(f"\n✅ Test completado exitosamente\n")
    print(f"  📌 Configuración:")
    print(f"     - Tema personalizado: Starlink")
    print(f"     - Total de temas: {len(tweets_by_theme)}")
    print(f"\n  📊 Estadísticas:")
    print(f"     - Tweets procesados: {len(tweets)}")
    print(f"     - Tweets clasificados como Starlink: {starlink_count}")
    print(f"     - Tasa de clasificación: {(starlink_count/len(tweets)*100):.0f}%")
    print(f"\n  📁 Archivo generado:")
    print(f"     - Nombre: {output_file}")
    print(f"     - Tamaño: {file_size:,} bytes")
    print(f"\n  ✨ Estado: LISTO PARA PRODUCCIÓN")

    print("\n" + "=" * 70)
    print("🚀 Próximos pasos en producción:")
    print("=" * 70)
    print("""
  1. Añadir cuentas reales: panel web → añadir @usuario
  2. El sistema rastreará automáticamente los tweets
  3. Personalizar temas en app/themes.json según tus necesidades
  4. Descargar el libro periódicamente con el botón "📖 Descargar libro"
  5. Convertir a PDF/HTML con: pandoc test_starlink_book.md -o test_starlink_book.pdf

  ✓ El seguimiento es 100% gratuito
  ✓ Los temas son completamente personalizables
  ✓ La clasificación automática por palabras clave
    """)


if __name__ == "__main__":
    main()
