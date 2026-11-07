import json
import logging
import urllib.request

from src.config import DISCORD_WEBHOOK_URL

LOGGER = logging.getLogger(__name__)

def notify_discord(paper: dict, webhook_url: str | None = None):
    webhook_url = DISCORD_WEBHOOK_URL if webhook_url is None else webhook_url
    if not webhook_url:
        LOGGER.info(f'no discord webhook, ignoring for {paper['filename']}')
        return
    message = f"New paper : **{paper['title']}**\nCategory : {paper['category']}\nFile : {paper['filename']}"
    payload = json.dumps({'content': message}).encode('utf-8')
    request = urllib.request.Request(
        webhook_url,
        data=payload,
        method='POST'
    )
    with urllib.request.urlopen(request, timeout=15) as response:
        if response.status not in (200, 204):
            raise RuntimeError(f'discord error : {response.status}')
