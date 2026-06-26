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

DEFAULT_MIU_INTERVAL = 5 * 60
DEFAULT_MAHI_INTERVAL = 46 * 60
DEFAULT_PISHI_INTERVAL = 3 * 60 * 60
DEFAULT_CASINO_INTERVAL = 6 * 60

miu_interval = DEFAULT_MIU_INTERVAL
mahi_interval = DEFAULT_MAHI_INTERVAL
pishi_interval = DEFAULT_PISHI_INTERVAL
casino_interval = DEFAULT_CASINO_INTERVAL

def parse_shekam(text):
    if not text:
        return None
    for line in text.split("\n"):
        if "شکم" in line:
            if "من گشنمیووو" in line:
                return "hungry"
            else:
                return "full"
    return None

def parse_mio_points(text):
    if not text:
        return None
    for line in text.split("\n"):
        if "میو پوینت" in line:
            if ":" in line:
                after_colon = line.split(":")[-1]
                numbers = re.findall(r'[\d,]+', after_colon)
                if numbers:
                    try:
                        return int(numbers[0].replace(",", ""))
                    except ValueError:
                        pass
    return None

def make_client(session_string):
    return TelegramClient(StringSession(session_string), API_ID, API_HASH)

async def run_client(session_string, client_name):
    global is_running, miu_interval, mahi_interval, pishi_interval, casino_interval
    pending = {}
    gorbe_clicks = {}
    client = make_client(session_string)

    await client.start()
    me = await client.get_me()

    async def click_gorbe_aggressive(msg_id):
        clicks = 0
        while clicks < 3:
            try:
                msg = await client.get_messages(GROUP_USERNAME, ids=msg_id)
                if not msg or not msg.buttons:
                    print(f"[{client_name}] gorbe: no button (click {clicks})")
                    break
                await msg.click(0)
                clicks += 1
                gorbe_clicks[msg_id] = clicks
                print(f"[{client_name}] gorbe: click {clicks} done")
                await asyncio.sleep(0.5)
            except Exception as e:
                print(f"[{client_name}] gorbe: error click {clicks+1}: {e}")
                await asyncio.sleep(0.5)

    async def do_casino(mio_points):
        try:
            casino_msg = await client.send_message(GROUP_USERNAME, "کازینو")
            print(f"[{client_name}] casino: sent 'کازینو'")
            await asyncio.sleep(3)

            # مرحله ۱: سه دکمه یک ردیفه - دکمه وسط 🎰
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            if not casino_msg or not casino_msg.buttons:
                print(f"[{client_name}] casino: no buttons step 1")
                return
            await casino_msg.click(0, 1)
            print(f"[{client_name}] casino: step 1 - clicked 🎰")
            await asyncio.sleep(3)

            # مرحله ۲: دو ردیف تک دکمه - دکمه بالا
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            if not casino_msg or not casino_msg.buttons:
                print(f"[{client_name}] casino: no buttons step 2")
                return
            await casino_msg.click(0, 0)
            print(f"[{client_name}] casino: step 2 - clicked top button")
            await asyncio.sleep(2)

            # مرحله ۳: ریپلای با mio_points
            await client.send_message(GROUP_USERNAME, str(mio_points), reply_to=casino_msg.id)
            print(f"[{client_name}] casino: step 3 - replied with {mio_points}")
            await asyncio.sleep(3)

            # مرحله ۴: دو ردیف تک دکمه - دکمه بالا
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            if not casino_msg or not casino_msg.buttons:
                print(f"[{client_name}] casino: no buttons step 4")
                return
            await casino_msg.click(0, 0)
            print(f"[{client_name}] casino: step 4 - clicked top button")
            await asyncio.sleep(3)

            # مرحله ۵: ردیف بالا سه دکمه - سمت چپ
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            if not casino_msg or not casino_msg.buttons:
                print(f"[{client_name}] casino: no buttons step 5")
                return
            await casino_msg.click(0, 0)
            print(f"[{client_name}] casino: step 5 - clicked left button")
            await asyncio.sleep(3)

            # مرحله ۶: دو ردیف تک دکمه - دکمه بالا
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            if not casino_msg or not casino_msg.buttons:
                print(f"[{client_name}] casino: no buttons step 6")
                return
            await casino_msg.click(0, 0)
            print(f"[{client_name}] casino: step 6 - clicked top button")
            await asyncio.sleep(3)

            # مرحله ۷: ریپلای با 🎰
            casino_msg = await client.get_messages(GROUP_USERNAME, ids=casino_msg.id)
            await client.send_message(GROUP_USERNAME, "🎰", reply_to=casino_msg.id)
            print(f"[{client_name}] casino: step 7 - replied with 🎰 done!")

        except Exception as e:
            print(f"[{client_name}] casino: error: {e}")

    @client.on(events.NewMessage(chats=GROUP_USERNAME))
    async def on_new_message(event):
        global is_running, miu_interval, mahi_interval, pishi_interval, casino_interval
        msg = event.message

        if event.sender_id == me.id:
            text = msg.text.strip() if msg.text else ""

            if text.lower() == "stop":
                is_running = False
                await client.send_message(GROUP_USERNAME, "متوقف شد ⛔")
                print(f"[{client_name}] stopped")
                return

            if text.lower() == "start":
                is_running = True
                await client.send_message(GROUP_USERNAME, "شروع شد ✅")
                print(f"[{client_name}] started")
                return

            if text.startswith("تنظیم میو "):
                parts = text.split()
                if parts[-1].lower() == "دیفالت":
                    miu_interval = DEFAULT_MIU_INTERVAL
                    await client.send_message(GROUP_USERNAME, f"✅ میو برگشت به دیفالت ({DEFAULT_MIU_INTERVAL // 60} دقیقه)")
                else:
                    try:
                        mins = int(parts[-1])
                        miu_interval = mins * 60
                        await client.send_message(GROUP_USERNAME, f"✅ میو هر {mins} دقیقه")
                    except ValueError:
                        await client.send_message(GROUP_USERNAME, "❌ فرمت اشتباه. مثال: تنظیم میو 10")
                return

            if text.startswith("تنظیم ماهی "):
                parts = text.split()
                if parts[-1].lower() == "دیفالت":
                    mahi_interval = DEFAULT_MAHI_INTERVAL
                    await client.send_message(GROUP_USERNAME, f"✅ ماهی برگشت به دیفالت ({DEFAULT_MAHI_INTERVAL // 60} دقیقه)")
                else:
                    try:
                        mins = int(parts[-1])
                        mahi_interval = mins * 60
                        await client.send_message(GROUP_USERNAME, f"✅ ماهی هر {mins} دقیقه")
                    except ValueError:
                        await client.send_message(GROUP_USERNAME, "❌ فرمت اشتباه. مثال: تنظیم ماهی 60")
                return

            if text.startswith("تنظیم پیشی "):
                parts = text.split()
                if parts[-1].lower() == "دیفالت":
                    pishi_interval = DEFAULT_PISHI_INTERVAL
                    await client.send_message(GROUP_USERNAME, f"✅ پیشی برگشت به دیفالت ({DEFAULT_PISHI_INTERVAL // 60} دقیقه)")
                else:
                    try:
                        mins = int(parts[-1])
                        pishi_interval = mins * 60
                        await client.send_message(GROUP_USERNAME, f"✅ پیشی هر {mins} دقیقه")
                    except ValueError:
                        await client.send_message(GROUP_USERNAME, "❌ فرمت اشتباه. مثال: تنظیم پیشی 180")
                return

            if text.startswith("تنظیم کازینو "):
                parts = text.split()
                if parts[-1].lower() == "دیفالت":
                    casino_interval = DEFAULT_CASINO_INTERVAL
                    await client.send_message(GROUP_USERNAME, f"✅ کازینو برگشت به دیفالت ({DEFAULT_CASINO_INTERVAL // 60} دقیقه)")
                else:
                    try:
                        mins = int(parts[-1])
                        casino_interval = mins * 60
                        await client.send_message(GROUP_USERNAME, f"✅ کازینو هر {mins} دقیقه")
                    except ValueError:
                        await client.send_message(GROUP_USERNAME, "❌ فرمت اشتباه. مثال: تنظیم کازینو 6")
                return

        if msg.text and "گربه خیابونی" in msg.text:
            print(f"[{client_name}] gorbe: new message, clicking!")
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
                print(f"[{client_name}] pishi: button 1 clicked")
        except Exception as e:
            print(f"[{client_name}] pishi: error: {e}")

    @client.on(events.MessageEdited(chats=GROUP_USERNAME))
    async def on_message_edited(event):
        msg = event.message

        if msg.text and "گربه خیابونی" in msg.text:
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
                shekam = task.get("shekam")
                if shekam == "hungry":
                    await msg.click(1)
                    print(f"[{client_name}] mahi: button 2 clicked (hungry)")
                else:
                    await msg.click(0)
                    print(f"[{client_name}] mahi: button 1 clicked (full)")
        except Exception as e:
            print(f"[{client_name}] mahi: error: {e}")

    async def send_miu():
        await asyncio.sleep(0)
        while True:
            if is_running:
                try:
                    await client.send_message(GROUP_USERNAME, "معو")
                    print(f"[{client_name}] miu sent")
                except Exception as e:
                    print(f"[{client_name}] miu error: {e}")
            await asyncio.sleep(miu_interval)

    async def send_pishi():
        await asyncio.sleep(30)
        while True:
            if is_running:
                try:
                    msg = await client.send_message(GROUP_USERNAME, "پیشی")
                    pending[msg.id] = {"type": "pishi"}
                    print(f"[{client_name}] pishi sent")
                except Exception as e:
                    print(f"[{client_name}] pishi error: {e}")
            await asyncio.sleep(pishi_interval)

    async def send_mahi():
        await asyncio.sleep(60)
        while True:
            if is_running:
                try:
                    check_msg = await client.send_message(GROUP_USERNAME, "پیشی")
                    print(f"[{client_name}] pishi check sent")
                    await asyncio.sleep(4)

                    shekam = None
                    async for bot_reply in client.iter_messages(GROUP_USERNAME, limit=15):
                        if bot_reply.reply_to and bot_reply.reply_to.reply_to_msg_id == check_msg.id:
                            shekam = parse_shekam(bot_reply.text)
                            print(f"[{client_name}] shekam: {shekam}")
                            break

                    msg = await client.send_message(GROUP_USERNAME, "ماهی")
                    pending[msg.id] = {"type": "mahi", "shekam": shekam}
                    print(f"[{client_name}] mahi sent")
                except Exception as e:
                    print(f"[{client_name}] mahi error: {e}")
            await asyncio.sleep(mahi_interval)

    async def send_casino():
        await asyncio.sleep(90)
        while True:
            if is_running:
                try:
                    mioham_msg = await client.send_message(GROUP_USERNAME, "میوهام")
                    print(f"[{client_name}] casino: sent 'میوهام'")
                    await asyncio.sleep(4)

                    mio_points = None
                    async for bot_reply in client.iter_messages(GROUP_USERNAME, limit=15):
                        if bot_reply.reply_to and bot_reply.reply_to.reply_to_msg_id == mioham_msg.id:
                            mio_points = parse_mio_points(bot_reply.text)
                            print(f"[{client_name}] casino: mio_points={mio_points}")
                            break

                    if mio_points is None:
                        print(f"[{client_name}] casino: could not find mio points, skipping")
                    else:
                        bet_amount = min(mio_points, 20000)
                        print(f"[{client_name}] casino: bet_amount={bet_amount}")
                        await do_casino(bet_amount)

                except Exception as e:
                    print(f"[{client_name}] casino loop error: {e}")
            await asyncio.sleep(casino_interval)

    print(f"[{client_name}] started")
    await asyncio.gather(
        send_miu(),
        send_pishi(),
        send_mahi(),
        send_casino(),
        client.run_until_disconnected(),
    )

async def main():
    await asyncio.gather(
        run_client(SESSION_STRING_1, "client1"),
        run_client(SESSION_STRING_2, "client2"),
    )

if __name__ == "__main__":
    asyncio.run(main())
