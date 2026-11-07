
"""Génère une page HTML simple pour afficher les articles."""
from pathlib import Path
from html import escape
from urllib.parse import quote

from src.config import OUTPUT_DIR
from src.database import list_papers


def render_html(papers: list[dict]) -> str:
    articles = []

    for paper in papers:
        titre = escape(paper["title"])
        resume = escape(paper["summary"])
        categorie = escape(paper["category"])
        mots_cles = escape(", ".join(paper["keywords"]))
        lien_pdf = "../papers/" + quote(paper["filename"])

        articles.append(f"""
        <article>
            <h2><a href="{escape(lien_pdf, quote=True)}">{titre}</a></h2>
            <p>{resume}</p>
            <p><b>Catégorie :</b> {categorie}</p>
            <p><b>Mots-clés :</b> {mots_cles}</p>
        </article>
        """)

    contenu = "\n".join(articles) if articles else "<p>Aucun article.</p>"

    return f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <title>Bibliothèque de recherche</title>
    <style>
        body {{ font-family: Arial; max-width: 800px; margin: 40px auto; }}
        input {{ width: 100%; padding: 10px; box-sizing: border-box; }}
        article {{ border-bottom: 1px solid #ccc; padding: 15px 0; }}
    </style>
</head>
<body>
    <h1>Bibliothèque de recherche</h1>
    <input id="recherche" placeholder="Rechercher..." oninput="rechercher()">
    <main>{contenu}</main>

    <script>
        function rechercher() {{
            const texte = document.getElementById('recherche').value.toLowerCase();
            document.querySelectorAll('article').forEach(article => {{
                article.hidden = !article.textContent.toLowerCase().includes(texte);
            }});
        }}
    </script>
</body>
</html>"""


def write_html(output_dir: Path = OUTPUT_DIR) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    fichier = output_dir / "index.html"
    fichier.write_text(render_html(list_papers()), encoding="utf-8")
    return str(fichier)
