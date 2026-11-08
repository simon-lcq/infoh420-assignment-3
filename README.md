# INFOH420, Assignment 3

## How it works

The `research_paper_pipeline` DAG (`dags/pipeline.py`) runs four tasks:

1. `scan_papers`, detects all pdf in the `papers/` folder that are not yet in the database (filenames are used as keys).
2. `process_papers`, converts each pdf to markdown with `pymupdf4llm`, then asks the LLM for a title, summary, keywords and category. Results are inserted into SQLite.
3. `regenerate_html`, regenerates the entire `output/index.html` from the database contents.
4. `send_notifications`, posts one discord message per new paper via a webhook, if one is configured.

## Repository layout

```
dags/pipeline.py          airflow dag (every 15 minutes)
src/config.py             paths and environment variables
src/convert.py            pdf detection, pymupdf4llm conversion
src/llm.py                metadata extraction via llm
src/database.py           sqlite (schema, inserts, listing)
src/html_generator.py     static html page generation
src/notifications.py      discord webhook
data/markdown/            markdown generated from the pdfs
docker-compose.yml        airflow 3.3.2 (standalone), port 8080 on localhost only
Dockerfile                airflow image + requirements (pymupdf4llm, openai)
```

## Configuration

Copy `.env.example` to `.env`:

| Variable | Purpose |
|---|---|
| `LIBRARY_DIR` | **required**, path to the google drive folder, containing `papers/` (pdfs) and `output/` (generated html) |
| `UID` | user id for volume permissions (default `1000`) |
| `OLLAMA_MODEL` | ollama model to use (default `llama3.2:3b`) |
| `DISCORD_WEBHOOK_URL` | optional Discord webhook; if empty, the notification is skipped |

The internal paths (`PAPERS_DIR`, `OUTPUT_DIR`, `DB_PATH`, `MARKDOWN_DIR`, `OLLAMA_BASE_URL`) already have defaults consistent with the compose file.

## Running it

Prerequisites: Docker, and an Ollama server running on the host with the desired model:

```sh
ollama pull llama3.2:3b
docker compose up --build
```

The container reaches Ollama through `host.docker.internal:11434` (mapped to the Docker gateway via `extra_hosts`). Airflow is only reachable locally at http://localhost:8080.

Once the library is in place, the DAG runs on its own. The HTML page is generated in `<LIBRARY_DIR>/output/index.html` and links to the PDFs through relative paths (`../papers/...`), which makes it usable directly from the synced folder.