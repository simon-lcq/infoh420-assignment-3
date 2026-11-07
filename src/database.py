import json
import sqlite3
from pathlib import Path

from src.config import DB_PATH

def connect(db_path: Path = DB_PATH) -> sqlite3.Connection:
    db_path = Path(db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(str(db_path), timeout=60)
    connection.row_factory = sqlite3.Row
    return connection

def init_db(db_path: Path = DB_PATH):
    with connect(db_path) as connection:
        connection.execute('''
            CREATE TABLE IF NOT EXISTS papers (
                filename TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                summary TEXT NOT NULL,
                keywords TEXT NOT NULL,
                category TEXT NOT NULL
            )
        ''')

def existing_filenames(db_path: Path = DB_PATH) -> set[str]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute('SELECT filename FROM papers').fetchall()
    return {row['filename'] for row in rows}

def save_paper(filename: str, metadata: dict, db_path: Path = DB_PATH) -> bool:
    init_db(db_path)
    with connect(db_path) as connection:
        cursor = connection.execute('''
            INSERT OR IGNORE INTO papers
                (filename, title, summary, keywords, category)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            filename,
            metadata['title'],
            metadata['summary'],
            json.dumps(metadata['keywords'], ensure_ascii=False),
            metadata['category'],
        ))
        return cursor.rowcount == 1 # file = ok

def list_papers(db_path: Path = DB_PATH) -> list[dict]:
    init_db(db_path)
    with connect(db_path) as connection:
        rows = connection.execute('''
            SELECT filename, title, summary, keywords, category
            FROM papers ORDER BY title COLLATE NOCASE, filename
        ''').fetchall()
    return [
        {**dict(row), 'keywords': json.loads(row['keywords'])}
        for row in rows
    ]
