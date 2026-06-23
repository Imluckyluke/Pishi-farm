import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING_1 = os.environ["SESSION_STRING_1"]
SESSION_STRING_2 = os.environ["SESSION_STRING_2"]
GROUP_USERNAME = int(os.environ["GROUP_USERNAME"])

is_running = True

def make_client(session_string):
    return TelegramClient(StringSession(session_string), API_ID, API_HASH)

async def run_client(session_string, client_name):
    global is_running
    mahi_counter = 0
    pending = {}
    client = make_client(session_string)

    await client.start()
    me = await client.get_me()

    @client.on(events.NewMessage(chats=GROUP_USERNAME))
    async def on_new_message(event):
        global is_running
        msg = event.message

        if event.sender_id == me.id:
            if msg.text and msg.text.strip().lower() == "stop":
                is_running = False
                print(f"[{client_name}] متوقف شد")
                return
            if msg.text and msg.text.strip().lower() == "start":
                is_running = True
                print(f"[{client_name}] شروع شد")
                return

        if not msg.reply_to:
            return
        replied_to_id = msg.reply_to.reply_to_msg_id
        if replied_to_id not in pending:
            return
        task = pending.get(replied_to_id)
        if not msg.buttons:
            return
        try:
            if task["type"] == "pishi":
                pending.pop(replied_to_id)
                await msg.click(0)
                print(f"[{client_name}] پیشی: دکمه اول کلیک شد")
        except Exception as e:
            print(f"[{client_name}] خطا در کلیک پیشی: {e}")

    @client.on(events.MessageEdited(chats=GROUP_USERNAME))
    async def on_message_edited(event):
        nonlocal mahi_counter
        msg = event.message
        if not msg.reply_to:
            return
        replied_to_id = msg.reply_to.reply_to_msg_id
        if replied_to_id not in pending:
            return
        task = pending.get(replied_to_id)
        if task["type"] != "mahi":
            return
        if not msg.buttons:
            return
        try:
            pending.pop(replied_to_id)
            mahi_counter += 1
            if mahi_counter % 5 == 0:
                await msg.click(1)
                print(f"[{client_name}] ماهی: دکمه دوم کلیک شد (بار {mahi_counter})")
            else:
                await msg.click(0)
                print(f"[{client_name}] ماهی: دکمه اول کلیک شد (بار {mahi_counter})")
        except Exception as e:
            print(f"[{client_name}] خطا در کلیک ماهی: {e}")

    async def send_miu():
        while True:
            if is_running:
                try:
                    await client.send_message(GROUP_USERNAME, "معو")
                    print(f"[{client_name}] میو ارسال شد")
                except Exception as e:
                    print(f"[{client_name}] خطا میو: {e}")
            await asyncio.sleep(5 * 60 + 30)

    async def send_mahi():
        await asyncio.sleep(10)
        while True:
            if is_running:
                try:
                    msg = await client.send_message(GROUP_USERNAME, "ماهی")
                    pending[msg.id] = {"type": "mahi"}
                    print(f"[{client_name}] ماهی ارسال شد")
                except Exception as e:
                    print(f"[{client_name}] خطا ماهی: {e}")
            await asyncio.sleep(60 * 60)

    async def send_pishi():
        await asyncio.sleep(5)
        while True:
            if is_running:
                try:
                    msg = await client.send_message(GROUP_USERNAME, "پیشی")
                    pending[msg.id] = {"type": "pishi"}
                    print(f"[{client_name}] پیشی ارسال شد")
                except Exception as e:
                    print(f"[{client_name}] خطا پیشی: {e}")
            await asyncio.sleep(30 * 60)

    print(f"[{client_name}] شروع به کار کرد...")
    await asyncio.gather(
        send_miu(),
        send_mahi(),
        send_pishi(),
        client.run_until_disconnected(),
    )

async def main():
    await asyncio.gather(
        run_client(SESSION_STRING_1, "client1"),
        run_client(SESSION_STRING_2, "client2"),
    )

if __name__ == "__main__":
    asyncio.run(main())
