import asyncio
import os
import re
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING_1 = os.environ["SESSION_STRING_1"]
SESSION_STRING_2 = os.environ["SESSION_STRING_2"]
GROUP_USERNAME = int(os.environ["GROUP_USERNAME"])

is_running = True

def parse_shekam(text):
    if not text:
        return None
    for line in text.split("\n"):
        if "شکم" in line:
            match = re.search(r'\((\d+)\s*/\s*(\d+)\)', line)
            if match:
                a = int(match.group(1))
                b = int(match.group(2))
                return b - a
    return None

def make_client(session_string):
    return TelegramClient(StringSession(session_string), API_ID, API_HASH)

async def run_client(session_string, client_name):
    global is_running
    pending = {}
    gorbe_clicks = {}  # msg_id: تعداد کلیک
    gorbe_counter = 0  # کانتر کل پیام‌های گربه خیابونی
    client = make_client(session_string)

    await client.start()
    me = await client.get_me()

    async def click_gorbe_aggressive(msg_id):
        clicks = 0
        while clicks < 3:
            try:
                msg = await client.get_messages(GROUP_USERNAME, ids=msg_id)
                if not msg or not msg.buttons:
                    print(f"[{client_name}] گربه: کلید نداره (کلیک {clicks})")
                    break
                await msg.click(0)
                clicks += 1
                gorbe_clicks[msg_id] = clicks
                print(f"[{client_name}] گربه: کلیک {clicks} زده شد")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[{client_name}] گربه: خطا کلیک {clicks+1}: {e}")
                await asyncio.sleep(0.5)

    @client.on(events.NewMessage(chats=GROUP_USERNAME))
    async def on_new_message(event):
        nonlocal gorbe_counter
        global is_running
        msg = event.message

        if event.sender_id == me.id:
            if msg.text and msg.text.strip().lower() == "stop":
                is_running = False
                await client.send_message(GROUP_USERNAME, "متوقف شد ⛔")
                print(f"[{client_name}] متوقف شد")
                return
            if msg.text and msg.text.strip().lower() == "start":
                is_running = True
                await client.send_message(GROUP_USERNAME, "شروع شد ✅")
                print(f"[{client_name}] شروع شد")
                return

        if msg.text and "گربه خیابونی" in msg.text:
            gorbe_counter += 1
            print(f"[{client_name}] گربه: پیام {gorbe_counter}")
            if gorbe_counter % 3 == 0:
                print(f"[{client_name}] گربه: نوبت کلیک!")
                asyncio.create_task(click_gorbe_aggressive(msg.id))
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
        msg = event.message

        if msg.text and "گربه خیابونی" in msg.text:
            # اگه این پیام قبلاً کلیک شده و هنوز به 3 نرسیده دوباره کلیک کن
            if msg.id in gorbe_clicks and gorbe_clicks[msg.id] < 3:
                asyncio.create_task(click_gorbe_aggressive(msg.id))
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
            if task["type"] == "mahi":
                pending.pop(replied_to_id)
                diff = task.get("diff")
                if diff is not None and diff > 2:
                    await msg.click(1)
                    print(f"[{client_name}] ماهی: دکمه دوم (اختلاف {diff})")
                else:
                    await msg.click(0)
                    print(f"[{client_name}] ماهی: دکمه اول (اختلاف {diff})")
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
            await asyncio.sleep(5 * 60)

    async def send_mahi():
        await asyncio.sleep(10)
        while True:
            if is_running:
                try:
                    check_msg = await client.send_message(GROUP_USERNAME, "پیشی")
                    print(f"[{client_name}] پیشی چک ارسال شد")
                    await asyncio.sleep(4)

                    diff = None
                    async for bot_reply in client.iter_messages(GROUP_USERNAME, limit=15):
                        if bot_reply.reply_to and bot_reply.reply_to.reply_to_msg_id == check_msg.id:
                            diff = parse_shekam(bot_reply.text)
                            print(f"[{client_name}] اختلاف شکم: {diff}")
                            break

                    msg = await client.send_message(GROUP_USERNAME, "ماهی")
                    pending[msg.id] = {"type": "mahi", "diff": diff}
                    print(f"[{client_name}] ماهی ارسال شد")
                except Exception as e:
                    print(f"[{client_name}] خطا ماهی: {e}")
            await asyncio.sleep(46 * 60)

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
            await asyncio.sleep(3 * 60 * 60)

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
