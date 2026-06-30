"""
Telegram -> Discord keyword forwarder.

Watches a specific PUBLIC Telegram CHANNEL, and forwards a message to Discord
only if it contains an EXACT keyword match (whole word, case-insensitive),
e.g. your friend tags posts with the word "discord" when he wants them shared.

Everything else in the channel is ignored.
"""

import os
import re
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("tg-keyword-bot")

# ---- Config (set these as Railway env vars) ----
API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION_STRING = os.environ.get("TG_SESSION_STRING", "")  # see note below

CHANNEL_USERNAME = os.environ["TG_CHANNEL_USERNAME"]  # e.g. "somechannel" (no @, no t.me/)
KEYWORD = os.environ.get("KEYWORD", "discord")        # exact word to match

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
DISCORD_ROLE_ID = os.environ.get("DISCORD_ROLE_ID", "")  # optional: role to ping

# Build a regex for EXACT whole-word match, case-insensitive
KEYWORD_PATTERN = re.compile(rf"\b{re.escape(KEYWORD)}\b", re.IGNORECASE)

client = TelegramClient(
    StringSession(SESSION_STRING) if SESSION_STRING else "session",
    API_ID,
    API_HASH,
)


def send_to_discord(author: str, text: str, link: str = None):
    role_ping = f"<@&{DISCORD_ROLE_ID}> " if DISCORD_ROLE_ID else ""
    content = f"{role_ping}**{author}**\n{text}"
    if link:
        content += f"\n{link}"

    payload = {"content": content[:1900]}
    if DISCORD_ROLE_ID:
        # Explicitly allow this role to be pinged, even if the role itself
        # has "Allow anyone to mention this role" turned off
        payload["allowed_mentions"] = {"parse": [], "roles": [DISCORD_ROLE_ID]}

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code >= 300:
            log.error(f"Discord webhook failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Discord webhook error: {e}")


@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):
    msg = event.message
    text = msg.message or ""

    if not text:
        return  # ignore media-only / empty messages

    # Exact keyword match
    if not KEYWORD_PATTERN.search(text):
        return

    link = f"https://t.me/{CHANNEL_USERNAME}/{msg.id}"
    log.info(f"Match found: {text[:80]}")
    send_to_discord(CHANNEL_USERNAME, text, link=link)


async def main():
    await client.start()
    # Make sure we're "joined" to the public channel so events fire
    await client.get_entity(CHANNEL_USERNAME)
    log.info(f"Watching channel '{CHANNEL_USERNAME}' for keyword '{KEYWORD}'...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
