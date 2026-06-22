import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING = os.environ["SESSION_STRING"]
GROUP_USERNAME = os.environ["GROUP_USERNAME"]

mahi_counter = 0
client = TelegramClient(StringSession(SESSION_STRING), API_ID, API_HASH)
pending = {}

@client.on(events.NewMessage(chats=GROUP_USERNAME))
async def on_new_message(event):
    global mahi_counter
    msg = event.message
    if not msg.reply_to:
        return
    replied_to_id = msg.reply_to.reply_to_msg_id
    if replied_to_id not in pending:
        return
    task = pending.pop(replied_to_id)
    if not msg.buttons:
        return
    try:
        if task["type"] == "pishi":
            await msg.click(0)
            print("پیشی: دکمه اول کلیک شد")
        elif task["type"] == "mahi":
            mahi_counter += 1
            if mahi_counter % 5 == 0:
                await msg.click(1)
                print(f"ماهی: دکمه دوم کلیک شد (بار {mahi_counter})")
            else:
                await msg.click(0)
                print(f"ماهی: دکمه اول کلیک شد (بار {mahi_counter})")
    except Exception as e:
        print(f"خطا در کلیک: {e}")

async def send_miu():
    while True:
        try:
            await client.send_message(GROUP_USERNAME, "میو")
            print("میو ارسال شد")
        except Exception as e:
            print(f"خطا میو: {e}")
        await asyncio.sleep(6 * 60)

async def send_mahi():
    await asyncio.sleep(10)
    while True:
        try:
            msg = await client.send_message(GROUP_USERNAME, "ماهی")
            pending[msg.id] = {"type": "mahi"}
            print("ماهی ارسال شد")
        except Exception as e:
            print(f"خطا ماهی: {e}")
        await asyncio.sleep(60 * 60)

async def send_pishi():
    await asyncio.sleep(5)
    while True:
        try:
            msg = await client.send_message(GROUP_USERNAME, "پیشی")
            pending[msg.id] = {"type": "pishi"}
            print("پیشی ارسال شد")
        except Exception as e:
            print(f"خطا پیشی: {e}")
        await asyncio.sleep(30 * 60)

async def main():
    await client.start()
    print("شروع به کار کرد...")
    await asyncio.gather(
        send_miu(),
        send_mahi(),
        send_pishi(),
        client.run_until_disconnected(),
    )

if __name__ == "__main__":
    asyncio.run(main())
