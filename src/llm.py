
import json
import logging
import time

from openai import OpenAI

from src.config import OLLAMA_BASE_URL, OLLAMA_MODEL

LOGGER = logging.getLogger(__name__)

SYSTEM_PROMPT = """
You extract metadata from scientific articles.

For the title : give the title of the article exactly how it's named.
Return ONLY a valid JSON object with these fields:
- title: string
- summary: string (short summary of the paper)
- keywords: array of strings
- category: string

Do not include Markdown or explanations.
Do not invent information.
"""

METADATA_SCHEMA = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "summary": {"type": "string"},
        "keywords": {
            "type": "array",
            "items": {"type": "string"}
        },
        "category": {"type": "string"}
    },
    "required": ["title", "summary", "keywords", "category"],
    "additionalProperties": False
}

def validate_metadata(value: object) -> dict:
    if not isinstance(value, dict):
        raise ValueError("the response is not a json object")

    for key in ("title", "summary", "keywords", "category"):
        if key not in value:
            raise ValueError(f"missing field : {key}")

    for key in ("title", "summary", "category"):
        if not isinstance(value[key], str) or not value[key].strip():
            raise ValueError(f"empty field : {key}")

    if (not isinstance(value["keywords"], list) or not all(
            isinstance(k, str) and k.strip()
            for k in value["keywords"]
        )):
        raise ValueError("keywords is not an array")

    return {
        "title": value["title"].strip(),
        "summary": value["summary"].strip(),
        "keywords": [k.strip() for k in value["keywords"]],
        "category": value["category"].strip(),
    }


def extract_metadata(markdown: str, filename: str) -> dict:
    if not markdown.strip():
        raise ValueError("empty markdown")

    client = OpenAI(
        base_url=OLLAMA_BASE_URL,
        api_key="ollama",
        timeout=480,
        max_retries=0,
    )

    excerpt = markdown[:24000]
    prompt = f"PDF filename: {filename}\n\nContent:\n{excerpt}"

    for attempt in range(2):
        try:
            result = client.chat.completions.create(
                model=OLLAMA_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                response_format={
                    "type": "json_schema",
                    "json_schema": {
                        "name": "paper_metadata",
                        "strict": True,
                        "schema": METADATA_SCHEMA
                    }
                },
                temperature=0,
            )

            raw = result.choices[0].message.content
            LOGGER.info("LLM raw response: %s", raw[:3000] if raw else None)
            if not raw:
                raise ValueError("empty response")

            metadata = json.loads(raw)
            return validate_metadata(metadata)

        except (ValueError, json.JSONDecodeError) as error:
            LOGGER.warning(
                "invalid metadata for %s, attempt %d/2: %s",
                filename,
                attempt + 1,
                error,
            )

            if attempt == 1:
                raise

            time.sleep(1)

    raise RuntimeError("no valid response")
