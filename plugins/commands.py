import os
import logging
import asyncio
from datetime import datetime, timedelta
from Script import script
from plugins.pm_filter import auto_filter
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, WebAppInfo
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id
from database.users_chats_db import db
from database.config_db import mdb
from info import CHANNELS, ADMINS, STREAM_BTN, WAIT_TIME, FREE_LIMIT, REQUEST_GROUP, LOG_CHANNEL, AD_IMG, AUTH_CHANNEL
from utils import is_subscribed, temp, replace_blacklist
from plugins.shortner import shortlink
from pyrogram.errors.exceptions.bad_request_400 import MessageTooLong
import re
import base64
import pytz
logger = logging.getLogger(__name__)

BATCH_FILES = {}
blacklist = script.BLACKLIST
waitime = WAIT_TIME

@Client.on_message(filters.command("search") & filters.user(ADMINS))
async def generate_link(client, message):
    command_text = message.text.split(maxsplit=1)
    if len(command_text) < 2:
        await message.reply("Please provide the name for the movie! Example: `/search game of thrones`")
        return
    movie_name = command_text[1].replace(" ", "-")
    link = f"https://telegram.me/{temp.U_NAME}?start=search-{movie_name}"
    
    await message.reply(
        text=f"Here is your link: {link}",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="Share Link", url=f"https://telegram.me/share/url?url={link}")]]
        )
    )
    
@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton("🔰 Bob Files 🔰", url="https://t.me/Bob_Files1")
            ]
            ]

        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup, disable_web_page_preview=True)
        await asyncio.sleep(2)
    term = await mdb.get_configuration_value("terms")
    if not await db.is_user_exist(message.from_user.id) and term and len(message.command) != 2:
        button = [
            [InlineKeyboardButton("📜 Read Terms", callback_data="terms")],
            [InlineKeyboardButton("✅ Accept", callback_data="home")]
            
        ]
        reply_markup = InlineKeyboardMarkup(button)
        await message.reply(
            f"<b>Welcome to our {temp.B_NAME} Bot! Before using our service, you agree to these Terms & Conditions. Please read them carefully.</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(message.from_user.id, message.from_user.mention))
    
    if len(message.command) != 2:
        buttons = [[
                    # InlineKeyboardButton('Refer', callback_data="refer"),
                     InlineKeyboardButton('Premium', callback_data="upgrd"),
                     InlineKeyboardButton(" ➕ Add To Your Group ➕", url='http://t.me/Bobfilterbot?startgroup=true')
                     ],[
                    InlineKeyboardButton('⚠️ ғᴇᴀᴛᴜʀᴇ', callback_data='help'),
                    InlineKeyboardButton('🌿 ᴀʙᴏᴜᴛ', callback_data='about')
                    ],[
                    InlineKeyboardButton('📕 sᴜᴘᴘᴏʀᴛ', web_app=WebAppInfo(url="https://qr-code-bob-files.vercel.app")),
                    InlineKeyboardButton('📩 ʀᴇᴏ̨ᴜᴇsᴛ', callback_data="request")
                  ]]
     #   buttons = [[
      #              InlineKeyboardButton('👥 Refer & Get Premium', callback_data="refer"),
       #             ],[
        #            InlineKeyboardButton('🔥 Trending', callback_data="trending")
         #           ],[
          #          InlineKeyboardButton('🎟️ Upgrade ', callback_data="upgrd"),
           #         InlineKeyboardButton('🗣️ Request', callback_data="request")
            #      ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_chat_action(enums.ChatAction.TYPING)
        # await asyncio.sleep(2)
        await message.reply_text(
            text=script.START_TXT.format(message.from_user.mention, temp.B_NAME),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        return
    data = message.command[1]
    forcesub = await mdb.get_configuration_value("forcesub")
    lifetime_files = await db.get_lifetime_files_count(message.from_user.id)
    """if not data.split("-", 1)[0] == "ReferID" and FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, message) and (lifetime_files is not None and lifetime_files >= 3): # forcesub limit 3
        # try:
            # invite_link = await client.create_chat_invite_link(int(FORCESUB_CHANNEL), creates_join_request=True)
        # except Exception as e:
        #     logger.error(e)
        btn = [
            [
                InlineKeyboardButton("🔰 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🔰", url="https://t.me/Bob_Files1")
            ]
        ]

        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub' 
                btn.append([InlineKeyboardButton("Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
        await client.send_message(
            chat_id=message.from_user.id,
            text="**Only Channel Subscriber Can Use This Bot**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
            )
        if not await db.is_user_exist(message.from_user.id):
            await db.add_user(message.from_user.id, message.from_user.first_name)
        ʀᴇᴛᴜʀɴ"""


    if len(message.command) == 2 and message.command[1].startswith('search'):
        movies = message.command[1].split("-", 1)[1]
        movie = movies.replace('-', ' ')
        message.text = movie
        text, button = await auto_filter(client, message)
        await message.reply(text=f"<b>{text}</b>", reply_markup=button, disable_web_page_preview=True)
        return
        
    if len(message.command) == 2 and message.command[1] in ["subscribe", "upgrade", "premium"]:
        buttons = [[
                InlineKeyboardButton('💫 pay', callback_data="confirm")
                ]]
        tnc= f"<a href=https://t.me/{temp.U_NAME}?start=terms>T&C apply</a>"
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_text(
            text=script.UPGRD_TXT.format(tnc),
            reply_markup=reply_markup,
            disable_web_page_preview=True
        )
        return
    
    if AUTH_CHANNEL and not await is_subscribed(client, message):
        # if not await db.find_join_req(message.from_user.id):
            # try:
            #     invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
            # except ChatAdminRequired:
            #     logger.error("Mᴀᴋᴇ sᴜʀᴇ Bᴏᴛ ɪs ᴀᴅᴍɪɴ ɪɴ Fᴏʀᴄᴇsᴜʙ ᴄʜᴀɴɴᴇʟ")
            #     return
            btn = [[
                # InlineKeyboardButton("Cʜᴀɴɴᴇʟ 1", url=f't.me/The_Happy_Hour_Hindi'),
                InlineKeyboardButton("Bob Files 🌿", url="https://t.me/bob_files1")
              ]]
    
            if message.command[1] != "subscribe":
                try:
                    kk, file_id = message.command[1].split("_", 1)
                    # temp.SAFARI_ID[message.from_user.id] = file_id
                    pre = 'checksubp' if kk == 'filep' else 'checksub' 
                    btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
                except (IndexError, ValueError):
                    btn.append([InlineKeyboardButton("↻ Tʀʏ Aɢᴀɪɴ", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
            await client.send_message(
                chat_id=message.from_user.id,
                text="**👉 First Join My Channel 📩\n👉 After Click On Try Again 🔰\n👉 And Get Gream Of Your Life 🥂**",
                reply_markup=InlineKeyboardMarkup(btn),
                parse_mode=enums.ParseMode.MARKDOWN
                )
            return
    
    if message.command[1] == "terms":
        button = [[InlineKeyboardButton('⛔️ Close', callback_data="close_data")]]
        await message.reply_text(text=script.TERMS, reply_markup=InlineKeyboardMarkup(button), disable_web_page_preview=True)
        return
    
    # showing ads
    if len(message.command) == 2 and message.command[1] in ["ads"]:
        msg, _, impression = await mdb.get_advirtisment()
        user = await db.get_user(message.from_user.id)
        seen_ads = user.get("seen_ads", False)
        STREAM_LINK = await db.get_stream_link()
        # buttons = [[
        #             InlineKeyboardButton('ᴄʟᴏꜱᴇ ❌', callback_data='close_data')
        #           ]]
        # reply_markup = InlineKeyboardMarkup(buttons)
        if msg:
            await message.reply_photo(
                photo=STREAM_LINK if STREAM_LINK else AD_IMG,
                caption=msg,
                # reply_markup=reply_markup,
                parse_mode=enums.ParseMode.HTML
            )
            if impression is not None and not seen_ads:
                await mdb.update_advirtisment_impression(int(impression) - 1)
                await db.update_value(message.from_user.id, "seen_ads", True)
        else:
            await message.reply("<b>No Ads Found</b>")
        await mdb.reset_advertisement_if_expired()
        if msg is None and seen_ads:
            await db.update_value(message.from_user.id, "seen_ads", False)
        return
        
    if message.command[1] == "trending":
        m = await message.reply_text(f"<b>Please wait, fetching trending searches...</b>")
        top_messages = await mdb.get_top_messages(30)

        truncated_messages = set()  # Use a set instead of a list
        for msg in top_messages:
            if msg.startswith('@'):  # Skip messages starting with '@'
                continue
            if len(msg) > 30:
                truncated_messages.add(msg[:30 - 3].lower().title() + "...")  # Convert to lowercase, capitalize and add to set
            else:
                truncated_messages.add(msg.lower().title())  # Convert to lowercase, capitalize and add to set

        keyboard = []
        for i in range(0, len(truncated_messages), 2):
            row = list(truncated_messages)[i:i+2]  # Convert set to list for indexing
            keyboard.append(row)

        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True, placeholder="Most searches of the day")
        await message.reply_text(f"<b>Here is the trending search...</b>", reply_markup=reply_markup)
        await m.delete()
        return
    
    # Refer
    if message.command[1] == "refer":
        m = await message.reply_text(f"<b>Generating your refferal link...</b>")
        user_id = message.from_user.id
        referral_points = await db.get_refferal_count(user_id)
        refferal_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{user_id}"
        keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Invite Your Friends", url=f"https://telegram.me/share/url?url={refferal_link}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83")]])
        reft=script.REFFERAL_TEXT.format(refferal_link)
        refferal_text = f"{reft}\n🌟Referral Points: {referral_points}"

        await m.edit(
            text=refferal_text,
            reply_markup=keyboard,
            disable_web_page_preview=True
        )
        return
    
    # Referral sysytem
    elif data.split("-", 1)[0] == "ReferID":
        invite_id = int(data.split("-", 1)[1])

        try:
            invited_user = await client.get_users(invite_id)
        except Exception as e:
            print(e)
            return

        if str(invite_id) == str(message.from_user.id):
            inv_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{message.from_user.id}"
            keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Invite Your Friends", url=f"https://telegram.me/share/url?url={inv_link}&text=%F0%9D%90%87%F0%9D%90%9E%F0%9D%90%A5%F0%9D%90%A5%F0%9D%90%A8!%20%F0%9D%90%84%F0%9D%90%B1%F0%9D%90%A9%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%A7%F0%9D%90%9C%F0%9D%90%9E%20%F0%9D%90%9A%20%F0%9D%90%9B%F0%9D%90%A8%F0%9D%90%AD%20%F0%9D%90%AD%F0%9D%90%A1%F0%9D%90%9A%F0%9D%90%AD%20%F0%9D%90%A8%F0%9D%90%9F%F0%9D%90%9F%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%AC%20%F0%9D%90%9A%20%F0%9D%90%AF%F0%9D%90%9A%F0%9D%90%AC%F0%9D%90%AD%20%F0%9D%90%A5%F0%9D%90%A2%F0%9D%90%9B%F0%9D%90%AB%F0%9D%90%9A%F0%9D%90%AB%F0%9D%90%B2%20%F0%9D%90%A8%F0%9D%90%9F%20%F0%9D%90%AE%F0%9D%90%A7%F0%9D%90%A5%F0%9D%90%A2%F0%9D%90%A6%F0%9D%90%A2%F0%9D%90%AD%F0%9D%90%9E%F0%9D%90%9D%20%F0%9D%90%A6%F0%9D%90%A8%F0%9D%90%AF%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%AC%20%F0%9D%90%9A%F0%9D%90%A7%F0%9D%90%9D%20%F0%9D%90%AC%F0%9D%90%9E%F0%9D%90%AB%F0%9D%90%A2%F0%9D%90%9E%F0%9D%90%AC.")]])
            await message.reply_text(f"<b>⚠️ You can't invite yourself, Send this invite link to your friends\n\nInvite Link</b> - \n<code>{inv_link}</code>",
                                    reply_markup=keyboard,
                                    disable_web_page_preview=True)
            return

        if not await db.is_user_exist(message.from_user.id):
            try:
                await db.add_user(message.from_user.id, message.from_user.first_name)
                await asyncio.sleep(1)
                referral = await db.get_refferal_count(invite_id) 
                await db.update_refferal_count(invite_id, referral + 10) 
                await client.send_message(text=f"You have successfully Invited {message.from_user.mention}", chat_id=invite_id)
                await message.reply_text(f"You have been successfully invited by {invited_user.first_name}", disable_web_page_preview=True)
            except Exception as e:
                logger.error(e)
        else:
            await message.reply_text("You already Invited or Joined")
        return
    
    # for counting each files for user
    files_counts = await db.fetch_value(message.from_user.id, "files_count") or 0
    lifetime_files = await db.get_lifetime_files_count(message.from_user.id)
    # optinal function for checking time difference between currrent time and next 12'o clock
    kolkata = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(kolkata)
    next_day = current_datetime + timedelta(days=1)
    next_day_midnight = datetime(next_day.year, next_day.month, next_day.day, tzinfo=kolkata)
    time_difference = (next_day_midnight - current_datetime).total_seconds() / 3600
    time_difference = round(time_difference)
    todays_date = current_datetime.strftime('%d%m%y')

    data = message.command[1].strip()
    if data.startswith(f"{temp.U_NAME}"):
        _, rest_of_data = data.split('-', 1)
        encypted_user_id, file_id = rest_of_data.split('_', 1)
        user_id_bytes = base64.urlsafe_b64decode(encypted_user_id)  # Decode from URL-safe base64
        userid = user_id_bytes.decode('utf-8')  # Convert bytes back to string
        
        files_ = await get_file_details(file_id)

        if not files_:
            return await message.reply(f"<b>No such file exists.</b>")
        
        Global_Link_Access = await mdb.get_configuration_value("global_link_access")
        if userid != str(message.from_user.id) and Global_Link_Access is False:
            return await message.reply(f"<b>You cannot access another person's request. Kindly submit your own request.</b>")
        
        files = files_[0]
        premium_status = await db.is_premium_status(message.from_user.id)
        shortner = await mdb.get_configuration_value("shortner")
        is_verified = await db.fetch_value(message.from_user.id, "verified")
        is_all_time_ads = await mdb.get_configuration_value("all_time_ad") 

        button = []
        button.append([
                InlineKeyboardButton("📩 All Channels", url=f"https://t.me/addlist/SCNstbbq9h42NTI1"),
                InlineKeyboardButton("🌿 ʙᴀᴄᴋᴜᴘ", url=f"https://t.me/Bob_Files1")
            ])
        
        if STREAM_BTN == True:
            button.append([
                InlineKeyboardButton("🖥️ ᴘʟᴀʏ ᴏɴʟɪɴᴇ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
            ])
            
        if premium_status is not True and files_counts is not None and files_counts >= 30:
                return await message.reply(f"<b>You have exceeded your daily free lmit. Please try after {time_difference} hours, or  <a href=https://t.me/{temp.U_NAME}?start=upgrade>Upgrade</a> To Premium For Unlimited Request.</b>", disable_web_page_preview=True)
        
        if is_all_time_ads is False and premium_status is not True and (is_verified is None or is_verified is False) and shortner != "no_shortner" and (lifetime_files is not None and lifetime_files >= FREE_LIMIT):
            # encoded date
            base64_date = str(todays_date).encode('utf-8')  # Convert to bytes
            encoded_todays_date = base64.urlsafe_b64encode(base64_date).decode('utf-8')
            # Encoded user_id
            user_id_bytes = str(message.from_user.id).encode('utf-8')  # Convert to bytes
            urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8')
            #verify link
            link = f"https://telegram.me/{temp.U_NAME}?start=Verify-{urlsafe_encoded_user_id}-{encoded_todays_date}"
            verifilink = await shortlink(link)
            logging.error(f"Shortner Error: {verifilink}")
            await message.reply_text(text='**First Follow This Importent Basic Steps\n\nStep 1 - Go To Telegram Settings\nStep 2 - Go To Chat Settings\nStep 3 - Turn Off "In-App Browser"\nStep 4 - Now Come Back On Bot\nStep 5 - Contiue To Your Verifiy\n\nFollow This Step One Time & Use Lifetime\nㅤ\nㅤ**')
            await asyncio.sleep(0.7)
            await message.reply_text(text='**You are not verified today ! Please verify now and get unlimited movie for full day..✔️\n\nTo use this bot you will have to do ᴠᴇʀɪғʏ otherwise you will not be able to use it..✖️\n\nRemove verification `-->` /premium**',
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("📩 ᴄʟɪᴄᴋ ᴛᴏ ᴠᴇʀɪғʏ", url=f"{verifilink}")],
                        [InlineKeyboardButton("🔰 ʜᴏᴡ ᴛᴏ ᴠᴇʀɪғʏ", url=f"telegram.me/kaisekhole/15")],
                        [InlineKeyboardButton('🎉 Remove Verification 🎉', callback_data="upgrd")],
                        # [InlineKeyboardButton("🔄 Chack My Verify", url=f"https://telegram.me/{temp.U_NAME}?start={temp.U_NAME}-{encypted_user_id}_{file_id}")]
                    ]),
                # disable_web_page_preview=True
            )
            return
        
        media_id=await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                caption=f"<b>{await replace_blacklist(files.caption or files.file_name, blacklist)}</b>",
                reply_markup=InlineKeyboardMarkup(button)
                )
        
        await db.update_value(message.from_user.id, "files_count", files_counts + 1)
        await db.update_value(message.from_user.id, "lifetime_files", lifetime_files + 1)
        del_msg = await client.send_message(
            text=f"<b>ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 ᴍɪɴ, sᴏ ғᴏʀᴡᴀʀᴅ ʏᴏᴜʀ-sᴇʟғ / ʏᴏᴜʀ-ғʀɪᴇɴᴅ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ᴀɴᴅ sᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇʀᴇ 🥂</b>",
            chat_id=message.from_user.id,
            reply_to_message_id=media_id.id)
        
        await asyncio.sleep(waitime or 600)
        await media_id.delete()
        return await del_msg.edit("__⊘ This message was deleted__")



    # Verify system
    elif data.split("-", 1)[0] == "Verify":
        user_id_b64, enc_date = data.split("-", 1)[1].split("-", 1)  # Correctly split the two base64 values

        #encode user_id
        user_id_bytes = str(message.from_user.id).encode('utf-8')  # Convert to bytes
        urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8')
        #decode user_id
        user_id_bytes = base64.urlsafe_b64decode(user_id_b64 + '==') 
        decoded_user_id = int(user_id_bytes.decode('utf-8'))  # Convert to bytes

        #encode data
        base64_date = str(todays_date).encode('utf-8')  # Convert to bytes
        encoded_todays_date = base64.urlsafe_b64encode(base64_date).decode('utf-8')
        #decode date
        decoded_date = base64.urlsafe_b64decode(enc_date + '=')
        safe_decoded_date = decoded_date.decode('utf-8')  # Convert to string
        
        #verify link
        verifi = f"https://telegram.me/{temp.U_NAME}?start=Verify-{urlsafe_encoded_user_id}-{encoded_todays_date}"
        verification = await shortlink(verifi)               
        is_verified = await db.fetch_value(message.from_user.id, "verified")

        if safe_decoded_date != todays_date:
            return await message.reply(
                text=f"<b>📌 Invalid verification link; Please click this button below to verify yourself.</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [InlineKeyboardButton("❇️ Verify", url=f"{verification}")]
                    ]),
                disable_web_page_preview=True
                )
        elif is_verified is True:
            return await message.reply("<b>Your Verification Allready Complete ✅\n\nNow Send Me Movie Name And Get File 📩</b>")
            # await client.send_message(LOG_CHANNEL, text=script.VERIFY2_TXT.format(message.from_user.mention)),
            # return
        elif decoded_user_id != message.from_user.id:
            return await message.reply("<b>Verification Unsuccessful; Try Again</b>")
        else:
            await db.update_value(message.from_user.id, "verified", True)
            await message.reply("<b>Your Today Verification Complete ✅\n\nNow Send Me Movie Name And Get File 📩</b>"),
            await client.send_message(LOG_CHANNEL, text=script.VERIFY2_TXT.format(message.from_user.mention)),
            return
                
    try:
        data = message.command[1].strip()
        try:
            pre, file_id = data.split('_', 1)
        except:
            file_id = data
            pre = ""

        files_ = await get_file_details(file_id)   
        if not files_:
            file_id = None
            try:
                pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("utf-16")).split("_", 1)
                msg = await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=file_id,
                )
                filetype = msg.media
                file = getattr(msg, filetype)
                title = file.file_name
                f_caption = f"<code>{title}</code>"
                await msg.edit_caption(f_caption)
                return
            except Exception as e:
                await message.reply(f'Error processing file: {e}')
            return await message.reply('No such file exist.')

        files = files_[0]
        title = files.file_name
        premium_status = await db.is_premium_status(message.from_user.id)
        button = []
        button.append([
                InlineKeyboardButton("📩 All Channels", url=f"https://t.me/addlist/SCNstbbq9h42NTI1"),
                InlineKeyboardButton("🌿 ʙᴀᴄᴋᴜᴘ", url=f"https://t.me/Bob_Files1")
            ])
        
        if STREAM_BTN == True:
            button.append([
                InlineKeyboardButton("🖥️ ᴘʟᴀʏ ᴏɴʟɪɴᴇ / ᴅᴏᴡɴʟᴏᴀᴅ 📥", callback_data=f"streaming#{file_id}")
            ])

        media_id=await client.send_cached_media(
            chat_id=message.from_user.id,
            file_id=file_id,
            caption=f"<b>{await replace_blacklist(files.caption or files.file_name, blacklist)}\n\nProvided By- @BoB_Files1</b>",
            reply_markup=InlineKeyboardMarkup(button)
            )
    
        # for counting each files for user
        files_counts = await db.fetch_value(message.from_user.id, "files_count") or 0
        lifetime_files = await db.fetch_value(message.from_user.id, "lifetime_files")
        await db.update_value(message.from_user.id, "files_count", files_counts + 1)
        await db.update_value(message.from_user.id, "lifetime_files", lifetime_files + 1)

        del_msg = await client.send_message(
            text=f"<b>ᴛʜɪs ғɪʟᴇ ᴡɪʟʟ ʙᴇ ᴅᴇʟᴇᴛᴇᴅ ᴡɪᴛʜɪɴ 5 ᴍɪɴ, sᴏ ғᴏʀᴡᴀʀᴅ ʏᴏᴜʀ-sᴇʟғ / ʏᴏᴜʀ-ғʀɪᴇɴᴅ ɪᴍᴍᴇᴅɪᴀᴛᴇʟʏ ᴀɴᴅ sᴛᴀʀᴛ ᴅᴏᴡɴʟᴏᴀᴅ ᴛʜᴇʀᴇ 🥂</b>",
            chat_id=message.from_user.id,
            reply_to_message_id=media_id.id)
    
        await asyncio.sleep(waitime or 600)
        await media_id.delete()
        return await del_msg.edit("__⊘ This message was deleted__")
    except Exception as e:
        logger.error(e)

        
@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
           
    """Send basic information of channel"""
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n@' + chat.username
        else:
            text += '\n' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    """Delete file from database"""
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to file with /delete which you want to delete', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not supported file format')
        return
    
    file_id, _ = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from database')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
            })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from database')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('File is successfully deleted from database')
            else:
                await msg.edit('File not found in database')


@Client.on_message(filters.command('deleteallfiles') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue??',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Hell No", callback_data="close_data"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Yes", callback_data="autofilter_delete"
                    )
                ],

                [
                    InlineKeyboardButton(
                        text="CANCEL", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def delete_multiple_files(bot, message):
    keyboard_buttons = [
        ["PreDVD", "PreDVDRip"],
        ["HDTS", "HDTC"],
        ["HDCam", "Sample"],
        ["CamRip", "Print"]
    ]

    btn = [
        [InlineKeyboardButton(button, callback_data=button.lower().replace("-", "")) for button in row]
        for row in keyboard_buttons
    ]
    btn.append(
        [InlineKeyboardButton("⛔️ Close", callback_data="close_data")]
        )

    await message.reply_text(
        text="<b>Select The Type Of Files You Want To Delete..?</b>",
        reply_markup=InlineKeyboardMarkup(btn),
        quote=True
    )


@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.message.edit('Succesfully Deleted All The Indexed Files.')

async def send_advirtisement(client, chat_id, msg_id, from_chat_id):
    try:
        await client.forward_messages(chat_id=chat_id, from_chat_id=from_chat_id, message_ids=msg_id, drop_author=True)
    except Exception as e:
        logger.error(e)

@Client.on_message(filters.command('stats'))
async def get_ststs(bot, message):
    rju = await message.reply('Fetching stats...')
    total_users = await db.total_users_count()
    files = await Media.count_documents()
    await rju.edit(script.STATUS_TXT.format(files, total_users))

@Client.on_message(filters.command('users') & filters.user(ADMINS))
async def list_users(bot, message):
    raju = await message.reply('Getting List Of Users')
    users = await db.get_all_users()
    out = "Users Saved In DB Are:\n\n"
    async for user in users:
        out += f"<a href=tg://user?id={user['id']}>{user['name']}</a>"
        if user['ban_status']['is_banned']:
            out += '( Banned User )'
        out += '\n'
    try:
        await raju.edit_text(out)
    except MessageTooLong:
        with open('users.txt', 'w+') as outfile:
            outfile.write(out)
        await message.reply_document('users.txt', caption="List Of Users")
