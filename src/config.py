import os
from pathlib import Path

PAPERS_DIR = Path(os.getenv('PAPERS_DIR', '/opt/airflow/library/papers'))
OUTPUT_DIR = Path(os.getenv('OUTPUT_DIR', '/opt/airflow/library/output'))
DB_PATH = Path(os.getenv('DB_PATH', '/opt/airflow/data/papers.db'))
MARKDOWN_DIR = Path(os.getenv('MARKDOWN_DIR', '/opt/airflow/data/markdown'))
OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://host.docker.internal:11434/v1')
OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'qwen3.5:4b-q4_K_M')
DISCORD_WEBHOOK_URL = os.getenv('DISCORD_WEBHOOK_URL', '')
