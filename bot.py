"""
Telegram -> Discord mirror.

Watches a specific PUBLIC Telegram CHANNEL and mirrors every text message
to a Discord channel via webhook. No keyword filtering, no role pings.
"""

import os
import asyncio
import logging
from telethon import TelegramClient, events
from telethon.sessions import StringSession
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("tg-mirror-bot")

# ---- Config (set these as Railway env vars) ----
API_ID = int(os.environ["TG_API_ID"])
API_HASH = os.environ["TG_API_HASH"]
SESSION_STRING = os.environ.get("TG_SESSION_STRING", "")

CHANNEL_USERNAME = os.environ["TG_CHANNEL_USERNAME"]  # e.g. "somechannel" (no @, no t.me/)

DISCORD_WEBHOOK_URL = os.environ["DISCORD_WEBHOOK_URL"]
DISCORD_WEBHOOK_NAME = os.environ.get("DISCORD_WEBHOOK_NAME", "Flyxes Call")
DISCORD_WEBHOOK_AVATAR = os.environ.get("DISCORD_WEBHOOK_AVATAR", "")  # optional avatar image URL

client = TelegramClient(
    StringSession(SESSION_STRING) if SESSION_STRING else "session",
    API_ID,
    API_HASH,
)


def send_to_discord(text: str):
    payload = {
        "content": text[:1900],
        "username": DISCORD_WEBHOOK_NAME,
        # Suppress every mention type so nothing in the mirrored text
        # can ping @everyone, @here, a role, or a user.
        "allowed_mentions": {"parse": []},
    }
    if DISCORD_WEBHOOK_AVATAR:
        payload["avatar_url"] = DISCORD_WEBHOOK_AVATAR

    try:
        resp = requests.post(DISCORD_WEBHOOK_URL, json=payload, timeout=10)
        if resp.status_code >= 300:
            log.error(f"Discord webhook failed: {resp.status_code} {resp.text}")
    except Exception as e:
        log.error(f"Discord webhook error: {e}")


@client.on(events.NewMessage(chats=CHANNEL_USERNAME))
async def handler(event):
    text = event.message.message or ""

    if not text.strip():
        return  # nothing to mirror (media-only / empty message)

    log.info(f"Mirroring: {text[:80]}")
    send_to_discord(text)


async def main():
    await client.start()
    # Make sure we're "joined" to the public channel so events fire
    await client.get_entity(CHANNEL_USERNAME)
    log.info(f"Mirroring all messages from '{CHANNEL_USERNAME}' to Discord...")
    await client.run_until_disconnected()


if __name__ == "__main__":
    asyncio.run(main())
