import asyncio
import aiohttp
import json
import os
from datetime import datetime

# ==================== НАСТРОЙКИ ====================
MATRIX_HOMESERVER = "https://synapse.wcomp.io"
MATRIX_TOKEN = os.getenv("MATRIX_TOKEN")
BOT_SENDER = "@bot:wcomp.io"
ROOM_ID = "!bifCqLQpAJmbqkCsdQ:wcomp.io"

TG_TOKEN = os.getenv("TG_TOKEN")
TG_CHAT_ID = os.getenv("TG_CHAT_ID")
# =================================================

async def send_to_telegram(session, text):
    url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
    try:
        await session.post(url, json={
            "chat_id": TG_CHAT_ID,
            "text": text,
            "parse_mode": "HTML"
        })
    except Exception as e:
        print(f"TG error: {e}")

async def matrix_poller():
    async with aiohttp.ClientSession() as session:
        since = ""
        print(f"[{datetime.now()}] Forwarder started...")

        while True:
            try:
                url = f"{MATRIX_HOMESERVER}/_matrix/client/v3/sync"
                params = {
                    "access_token": MATRIX_TOKEN,
                    "since": since,
                    "timeout": 30000,
                }

                async with session.get(url, params=params, timeout=40) as resp:
                    if resp.status != 200:
                        await asyncio.sleep(10)
                        continue

                    data = await resp.json()
                    since = data.get('next_batch', since)

                    for room_id, room_data in data.get('rooms', {}).get('join', {}).items():
                        if room_id != ROOM_ID:
                            continue

                        for event in room_data.get('timeline', {}).get('events', []):
                            if event.get('type') != 'm.room.message':
                                continue
                            if event.get('sender') != BOT_SENDER:
                                continue

                            body = event.get('content', {}).get('body', '')
                            if body:
                                await send_to_telegram(session, f"🤖 <b>Bot:</b>\n{body}")

            except Exception as e:
                print(f"Error: {e}")
                await asyncio.sleep(5)

# Для запуска в фоне
if __name__ == "__main__":
    asyncio.run(matrix_poller())
