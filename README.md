# Telegram Channel Keyword Forwarder Bot

Watches a **public Telegram channel** and forwards a post to Discord only when
it contains the exact word **"discord"** (whole word, case-insensitive) — so
your friend just tags the calls he wants shared, and everything else in the
channel stays out of Discord.

## How it works
- Uses Telethon (a Telegram **user session**, not a bot account) to read the
  public channel. This works even if you're just a regular subscriber.
- Matches the keyword as a **whole word** via regex `\bdiscord\b`, so it won't
  accidentally match something like "discordant" — only standalone "discord".
- Forwards matching post text + a link back to the original message.

## Setup

### 1. Telegram API credentials
If you already have `TG_API_ID` / `TG_API_HASH` / `TG_SESSION_STRING` set up
for your whale watch bot (same Telegram account), **reuse those** — no need
to regenerate. Otherwise:
- Get `api_id`/`api_hash` from https://my.telegram.org -> API Development Tools
- Run locally once:
  ```
  pip install telethon
  python generate_session.py
  ```
  Log in with your phone number + code, copy the printed session string.

### 2. Get the channel username
If the channel link is `https://t.me/somechannel`, the username is
`somechannel` (no `@`, no `t.me/`).

### 3. Create a Discord webhook
Discord -> Channel Settings -> Integrations -> Webhooks -> New Webhook -> copy URL.

### 4. Set environment variables
```
TG_API_ID=123456
TG_API_HASH=abcdef123456...
TG_SESSION_STRING=<from step 1, or reused from whale watch bot>
TG_CHANNEL_USERNAME=somechannel
KEYWORD=discord
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 5. Run locally to test
```
pip install -r requirements.txt
python bot.py
```
Ask your friend to post a test message containing the word "discord" and
confirm it shows up in your Discord channel.

### 6. Deploy to Railway
- Push this folder to a GitHub repo (or use the Railway CLI).
- New Railway project from the repo.
- Add the env vars above in Railway's Variables tab.
- Start command: `python bot.py` (Railway should auto-detect Python).
- No persistent volume needed — `TG_SESSION_STRING` handles auth.

## Notes
- Keep `TG_API_HASH` and `TG_SESSION_STRING` private — they're equivalent to
  a login to your Telegram account.
- If your friend later wants multiple trigger words, just change `KEYWORD`
  matching to a list — say the word and I'll update it.
- If the channel ever goes private or restricts joining, you may need to join
  it manually once with this same Telegram account before the bot can read it.
