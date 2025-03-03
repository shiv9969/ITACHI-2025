import logging
from pyrogram import Client, __version__
from database.ia_filterdb import Media
from database.users_chats_db import db
from info import API_ID, API_HASH, BOT_TOKEN
from utils import temp
from typing import Union, Optional, AsyncGenerator
from pyrogram import types
from aiohttp import web
from flask import Flask
import os


class Bot(Client):

    def __init__(self):
        super().__init__(
            name="autofilter",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            workers=200,
            plugins={"root": "plugins"},
            sleep_threshold=5,
        )

    async def start(self):
        b_users = await db.get_banned()
        temp.BANNED_USERS = b_users
        await super().start()
        await Media.ensure_indexes()
        me = await self.get_me()
        temp.BOT = self
        temp.ME = me.id
        temp.U_NAME = me.username
        temp.B_NAME = me.first_name
        self.username = '@' + me.username
        print(f"{temp.U_NAME} start ✅")
        logging.info(f"Bot started")

        app = web.AppRunner(await web_server())  # Removed incorrect "web-server" line
        await app.setup()
        port = 5054  # Changed from string to integer
        await web.TCPSite(app, "0.0.0.0", port).start()  # Fixed indentation

    async def stop(self, *args):
        await super().stop()
        logging.info("Bot stopped.")
    
    async def iter_messages(
        self,
        chat_id: Union[int, str],
        limit: int,
        offset: int = 0,
    ) -> Optional[AsyncGenerator["types.Message", None]]:
        current = offset
        while True:
            new_diff = min(200, limit - current)
            if new_diff <= 0:
                return
            messages = await self.get_messages(chat_id, list(range(current, current+new_diff+1)))
            for message in messages:
                yield message
                current += 1
                
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

app = Bot()
app.run() 
