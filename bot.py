import asyncio
import os
from telethon import TelegramClient, events
from telethon.sessions import StringSession

API_ID = int(os.environ["API_ID"])
API_HASH = os.environ["API_HASH"]
SESSION_STRING_1 = os.environ["SESSION_STRING_1"]
GROUP_USERNAME = int(os.environ["GROUP_USERNAME"])

def make_client(session_string):
    return TelegramClient(StringSession(session_string), API_ID, API_HASH)

async def main():
    pending = {}
    client = make_client(SESSION_STRING_1)
    await client.start()
    me = await client.get_me()
    print(f"logged in as {me.username}")

    @client.on(events.NewMessage(chats=GROUP_USERNAME))
    async def on_new(event):
        msg = event.message
        if not msg.reply_to:
            return
        replied_to_id = msg.reply_to.reply_to_msg_id
        if replied_to_id not in pending:
            return

        task = pending[replied_to_id]
        print(f"\n--- NEW msg id={msg.id} step={task['step']} ---")
        if msg.buttons:
            for i, row in enumerate(msg.buttons):
                for j, btn in enumerate(row):
                    print(f"  button ({i},{j}): '{btn.text}'")
        else:
            print("  no buttons!")
        print(f"  text: {msg.text[:200] if msg.text else 'none'}")

        await handle_casino(msg, pending, replied_to_id, task, client)

    @client.on(events.MessageEdited(chats=GROUP_USERNAME))
    async def on_edited(event):
        msg = event.message
        if not msg.reply_to:
            return
        replied_to_id = msg.reply_to.reply_to_msg_id
        if replied_to_id not in pending:
            return

        task = pending[replied_to_id]
        print(f"\n--- EDITED msg id={msg.id} step={task['step']} ---")
        if msg.buttons:
            for i, row in enumerate(msg.buttons):
                for j, btn in enumerate(row):
                    print(f"  button ({i},{j}): '{btn.text}'")
        else:
            print("  no buttons!")
        print(f"  text: {msg.text[:200] if msg.text else 'none'}")

        await handle_casino(msg, pending, replied_to_id, task, client)

    async def handle_casino(msg, pending, replied_to_id, task, client):
        step = task["step"]
        try:
            if step == 1:
                if not msg.buttons:
                    print("  waiting for buttons...")
                    return
                clicked = False
                for i, row in enumerate(msg.buttons):
                    for j, btn in enumerate(row):
                        if "🎰" in btn.text:
                            await msg.click(i, j)
                            clicked = True
                            print(f"  clicked 🎰 at ({i},{j})")
                            break
                    if clicked:
                        break
                if not clicked:
                    print("  🎰 NOT FOUND - skipping step")
                    return
                task["step"] = 2

            elif step == 2:
                if not msg.buttons:
                    print("  waiting for buttons...")
                    return
                await msg.click(0, 0)
                print(f"  clicked (0,0) - top button")
                await asyncio.sleep(1)
                await client.send_message(GROUP_USERNAME, str(task["mio_points"]), reply_to=msg.id)
                print(f"  replied with {task['mio_points']}")
                task["step"] = 3

            elif step == 3:
                if not msg.buttons:
                    print("  waiting for buttons...")
                    return
                await msg.click(0, 0)
                print(f"  clicked (0,0) - top button")
                task["step"] = 4

            elif step == 4:
                if not msg.buttons:
                    print("  waiting for buttons...")
                    return
                await msg.click(0, 0)
                print(f"  clicked (0,0) - left button")
                task["step"] = 5

            elif step == 5:
                if not msg.buttons:
                    print("  waiting for buttons...")
                    return
                await msg.click(0, 0)
                print(f"  clicked (0,0) - top button")
                task["step"] = 6

            elif step == 6:
                await client.send_message(GROUP_USERNAME, "🎰", reply_to=msg.id)
                pending.pop(replied_to_id)
                print(f"  replied with 🎰 - DONE!")

        except Exception as e:
            print(f"  error at step {step}: {e}")

    # ارسال کازینو
    casino_msg = await client.send_message(GROUP_USERNAME, "کازینو")
    print(f"sent 'کازینو' id={casino_msg.id}")
    pending[casino_msg.id] = {"type": "casino", "step": 1, "mio_points": 500}

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
