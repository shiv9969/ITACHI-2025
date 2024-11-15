# This code has been modified by @Safaridev
# Please do not remove this credit
from pyrogram import Client, filters, enums
from pyrogram.types import ChatJoinRequest, InlineKeyboardButton, InlineKeyboardMarkup
from database.users_chats_db import db
from Script import script
from database.ia_filterdb import get_file_details
from info import ADMINS, AUTH_CHANNEL
from utils import temp, get_size, replace_blacklist
import logging
blacklist = script.BLACKLIST
logger = logging.getLogger(__name__)

@Client.on_chat_join_request(filters.chat(AUTH_CHANNEL))
async def join_reqs(client, message: ChatJoinRequest):
    user_id = message.from_user.id
    file_id = temp.SAFARI_ID[user_id] 
    if not await db.find_join_req(user_id):
        await db.add_join_req(user_id)
        files_ = await get_file_details(file_id)   
        files = files_[0]
        title = files.file_name
        premium_status = await db.is_premium_status(message.from_user.id)
        button = [[
            InlineKeyboardButton("Sʜᴇʀᴇ Tʜɪs Bᴏᴛ 📩", url="https://t.me/share/url?url=Get%20Movie%20Easily%20To%20Following%203%20Step%20%E2%9C%A8%0A%0ASetp%201%20-%20Start%20This%20Bot%20%E2%9A%A1%0AStep%202%20-%20Send%20Movie%20Name%20%F0%9F%93%A9%0AStep%203%20-%20Get%20Directly%20Movie%20File%20%E2%9C%85%0A%0ABot%20Link%20-%20t.me%2FTHHREQROBOT%20%F0%9F%87%AE%F0%9F%87%B3")
            ]]
        if premium_status is True:
            button.append([InlineKeyboardButton("📱 Watch & Download", callback_data=f"download#{file_id}")])

        await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,

            caption=f"<b>{await replace_blacklist(files.caption or files.file_name, blacklist)}</b>",
            reply_markup=InlineKeyboardMarkup(button)
            )

@Client.on_message(filters.command("delreq") & filters.private & filters.user(ADMINS))
async def del_requests(client, message):
    try:
        await db.del_join_req()    
        await message.reply("<b>sᴜᴄssᴇғᴜʟʟʏ sᴀᴠᴇᴅ ʀᴇǫᴜᴇsᴛ ᴅᴇʟᴇᴛᴇᴅ ғʀᴏᴍ ᴅᴀᴛᴀʙᴀsᴇ ✅</b>")
    except Exception as e:
        await message.reply(f'{e}') 
    
