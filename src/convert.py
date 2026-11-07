import os
import tempfile
from pathlib import Path
import pymupdf4llm

from src.config import MARKDOWN_DIR, PAPERS_DIR
from src.database import existing_filenames

def find_pdfs(papers_dir: Path = PAPERS_DIR) -> list[str]:
    papers_dir = Path(papers_dir)
    papers_dir.mkdir(parents=True, exist_ok=True)
    known = existing_filenames()
    return sorted(
        p.name for p in papers_dir.iterdir() if p.is_file and p.suffix.lower() == '.pdf' and p.name not in known # check existence
    )

def pdf_to_markdown(filename: str, papers_dir: Path = PAPERS_DIR, markdown_dir: Path = MARKDOWN_DIR) -> str:
    if Path(filename).name != filename or Path(filename).suffix.lower() != '.pdf':
        raise ValueError(f'not a valid pdf : {filename}')
    pdf_file = Path(papers_dir) / filename
    if not pdf_file.is_file():
        raise FileNotFoundError(pdf_file)

    markdown = pymupdf4llm.to_markdown(str(pdf_file))
    if not isinstance(markdown, str) or not markdown.strip():
        raise ValueError(f'no text in {filename}')

    output_dir = Path(markdown_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / (filename + '.md')
    # to avoid partial markdown in case of crash
    fd, tmp = tempfile.mkstemp(prefix='.paper-', suffix='.md', dir=output_dir)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as handle:
            handle.write(markdown)
        os.replace(tmp, output_file)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)
    return markdown
