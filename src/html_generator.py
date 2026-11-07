from pathlib import Path
from html import escape
from urllib.parse import quote

from src.config import OUTPUT_DIR
from src.database import list_papers


def render_html(papers: list[dict]) -> str:
    articles = []

    for paper in papers:
        title = escape(paper["title"])
        summary = escape(paper["summary"])
        category = escape(paper["category"])
        keywords = escape(", ".join(paper["keywords"]))
        pdf_url = "../papers/" + quote(paper["filename"])

        articles.append(f"""
        <article>
            <h2><a href="{escape(pdf_url, quote=True)}">{title}</a></h2>
            <p>{summary}</p>
            <p><b>Category:</b> {category}</p>
            <p><b>Keywords:</b> {keywords}</p>
        </article>
        """)

    content = "\n".join(articles) or "<p>No papers found.</p>"

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Library</title>
    <style>
        body {{ font-family: Arial, sans-serif; max-width: 800px; margin: 40px auto; }}
        input {{ width: 100%; padding: 10px; box-sizing: border-box; }}
        article {{ border-bottom: 1px solid #ccc; padding: 15px 0; }}
    </style>
</head>
<body>
    <h1>Library</h1>
    <input id="search" type="search" placeholder="Search papers...">
    <main id="papers">{content}</main>

    <script>
        const container = document.getElementById("papers");
        const articles = [...container.querySelectorAll("article")];

        document.getElementById("search").addEventListener("input", (event) => {{
            const query = event.target.value.trim().toLowerCase();

            const ranked = articles.map(article => {{
                const title = article.querySelector("h2").textContent.toLowerCase();
                const content = article.textContent.toLowerCase();

                const rank = title.includes(query) ? 0 : content.includes(query) ? 1 : 2;
                return {{ article, rank }};
            }});

            ranked.sort((a, b) => a.rank - b.rank);

            ranked.forEach(({{ article, rank }}) => {{
                article.hidden = rank === 2;
                container.appendChild(article);
            }});
        }});
    </script>
</body>
</html>"""


def write_html(output_dir: Path = OUTPUT_DIR) -> str:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    file = output_dir / "index.html"
    file.write_text(render_html(list_papers()), encoding="utf-8")
    return str(file)