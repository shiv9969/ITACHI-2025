import asyncio, re, math, time, base64, pytz, aiohttp, ast, random, logging
from datetime import datetime, timedelta
from urllib.parse import quote
from Script import script
from info import AUTH_GROUPS, ADMINS, FORCESUB_CHANNEL, BIN_CHANNEL, URL, STREAM_MODE, REQUEST_GROUP, REDEEM_BASE_URL, REDEEM_ACCESS_KEY as ACCESS_KEY
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, WebAppInfo
from pyrogram import Client, filters, enums
from database.users_chats_db import db
from database.config_db import mdb
from pyrogram.errors import MessageNotModified
from utils import get_size, is_subscribed, search_gagala, temp, replace_blacklist, fetch_quote_content, stream_site
from database.ia_filterdb import Media, get_file_details, get_search_results
from database.filters_mdb import find_filter
from plugins.shortner import shortlink
from urllib.parse import quote_plus
from plugins.file_properties import get_name, get_hash

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_callback_query(filters.regex(r"^streaming"))
async def stream_download(bot, query):
    try:
        _, file_id = query.data.split('#', 1)
        user_id = query.from_user.id
        username =  query.from_user.mention 
        msg = await bot.send_cached_media(
            chat_id=BIN_CHANNEL,
            file_id=file_id)
            
        STREAM_CAP = """**ऑनलाइन देखने के लिए MX Player / VLC Player USE करे !!**"""

        online = f"{URL}watch/{str(msg.id)}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
        download = f"{URL}{str(msg.id)}/{quote_plus(get_name(msg))}?hash={get_hash(msg)}"
        non_online = await stream_site(online)
        non_download = await stream_site(download)
        if STREAM_MODE:
            await msg.reply_text(text=f"Name - {username}\n\nLink - tg://openmessage?user_id={user_id}\n\nSTREAM SHORT - ON ✅",
                reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=non_download),
                        InlineKeyboardButton("ᴘʟᴀʏ ᴏɴʟɪɴᴇ 🖥️", url=non_online)]]))
            k=await query.message.reply_text("🎉")
            await asyncio.sleep(1)
            await k.delete()
            await query.message.reply_text(
                text=f"{STREAM_CAP}\n\n**📥 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ - {non_download}\n\n🖥️ ᴘʟᴀʏ ᴏɴʟɪɴᴇ - {non_online}**",
                quote=True,
                reply_markup=InlineKeyboardMarkup([[
                    #     InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=non_download),
                    #     InlineKeyboardButton("ᴘʟᴀʏ ᴏɴʟɪɴᴇ 🖥️", url=non_online)
                    # ],[
                        InlineKeyboardButton('🎏 ʜᴏᴡ ᴛᴏ ᴘʟᴀʏ / ᴅᴏᴡɴʟᴏᴀᴅ 🎏', url='https://t.me/Bob_Files1')]]))
            return
        else:
            await msg.reply_text(text=f"Name - {username}\n\nLink - tg://openmessage?user_id={user_id}\n\nSHORT SHORT - OFF ❌",
                reply_markup=InlineKeyboardMarkup([[
                        InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download),
                        InlineKeyboardButton(" ᴘʟᴀʏ ᴏɴʟɪɴᴇ 🖥️", url=online)]]))
            k=await query.message.reply_text("🎉")
            await asyncio.sleep(1)
            await k.delete()
            await query.message.reply_text(
                text=f"{STREAM_CAP}\n\n**📥 ғᴀsᴛ ᴅᴏᴡɴʟᴏᴀᴅ - {download}\n\n🖥️ ᴘʟᴀʏ ᴏɴʟɪɴᴇ - {online}**",
                quote=True,
                reply_markup=InlineKeyboardMarkup([[
                    #     InlineKeyboardButton("📥 ᴅᴏᴡɴʟᴏᴀᴅ", url=download),
                    #     InlineKeyboardButton("ᴘʟᴀʏ ᴏɴʟɪɴᴇ 🖥️", url=online)
                    # ],[
                        InlineKeyboardButton('⁉️ ᴄʟᴏsᴇ ⁉️', callback_data='close_data')]]))
    except Exception as e:
        await query.answer(f'{e}', show_alert=True)   

@Client.on_message(filters.private & filters.text & filters.incoming)
async def filters_private_handlers(client, message):

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    if message.text.startswith(("/", "@")):
        return
    
    url_pattern = re.compile(r'https?://\S+')
    if message.from_user.id not in ADMINS:
        if re.search(url_pattern, message.text):
            await message.delete()
            return
            

    now = datetime.now()
    tody = int(now.timestamp())
    user_id = message.from_user.id
    user = await db.get_user(user_id)
    user_timestamps = user.get("timestamps")
    files_counts = user.get("files_count")
    premium_status = await db.is_premium_status(user_id)
    last_reset = user.get("last_reset")
    referral = await db.fetch_value(user_id, "referral")
    lifetime_files_count = user.get("lifetime_files")

    kolkata = pytz.timezone('Asia/Kolkata')
    current_datetime = datetime.now(kolkata)
    next_day = current_datetime + timedelta(days=1)
    next_day_midnight = datetime(next_day.year, next_day.month, next_day.day, tzinfo=kolkata)
    time_difference = (next_day_midnight - current_datetime).total_seconds() / 3600
    time_difference = round(time_difference)
    today = datetime.now(kolkata).strftime("%Y-%m-%d")

    maintenance_mode = await mdb.get_configuration_value("maintenance_mode")
    private_filter = await mdb.get_configuration_value("private_filter")
    forcesub = await mdb.get_configuration_value("forcesub")

    # update top messages
    await mdb.update_top_messages(message.from_user.id, message.text)
    if current_datetime.day in [7, 14, 21, 28]:
        await mdb.delete_all_messages()

    if last_reset != today:
        await db.reset_all_files_count()
        await db.reset_verification_status()        
         
    invite_link = None
    if FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, message) and lifetime_files_count is not None and lifetime_files_count >= 3:
        # try:
        #     invite_link = await client.create_chat_invite_link(int(FORCESUB_CHANNEL), creates_join_request=True)
        # except Exception as e:
        #     logger.error(e)
        if invite_link:
            btn = [
                [InlineKeyboardButton("🔰 ᴊᴏɪɴ ᴄʜᴀɴɴᴇʟ 🔰", url="https://t.me/bob_Files1")],
                [InlineKeyboardButton("Try again", callback_data="checkjoin")]
            ]
            await message.reply_text(
                f"<b>only channel subscriber can use this bot.</b>\nPlease join my channel to use this bot",
                reply_markup=InlineKeyboardMarkup(btn),
            )
        return
    
    # if referral >= 30 and premium_status is False:
    #     await db.update_value(user_id, "referral", referral - 30)
    #     await db.add_user_as_premium(user_id, 28, tody)
    #     await message.reply_text(f"**Congratulations! {message.from_user.mention},\nYou have received 1 month premium subscription for inviting 3 users.**", disable_web_page_preview=True)
    #     # send message to log channel
    #     await client.send_message(LOG_CHANNEL, f"{message.from_user.mention} <code>{message.from_user.id}</code> successfully received premium for inviting 3 users.")
    #     return
    
    if maintenance_mode is True:
        await message.reply_text(f"<b>Sorry for the inconvenience, we are under maintenance. We'll be back again soon!</b>", disable_web_page_preview=True)
        # await message.reply_text(f"<b>Bot Is Under Maintenance ⛑\n\nUse New Bot - @THHREQROBOT\nUse New Bot - @THHREQROBOT\nUse New Bot - @THHREQROBOT \n\n <code>------ OR ------</code>\n\nJoin Group - @ThappyHour\nJoin Group - @ThappyHour")
        return
    
    if private_filter is False:
        await message.reply_text(f"<b>Tᴇᴍᴘᴏʀᴀʀʏ ʙᴏᴛ ᴄᴀɴ'ᴛ ᴡᴏʀᴋɪɴɢ ʜᴇʀᴇ....⚠️\n\n<a href='https://t.me/thappyhour'>Rᴇᴏ̨ᴜᴇsᴛ Hᴀʀᴇ - t.me/thappyhour\nRᴇᴏ̨ᴜᴇsᴛ Hᴀʀᴇ - t.me/thappyhour\nRᴇᴏ̨ᴜᴇsᴛ Hᴀʀᴇ - t.me/thappyhour</a>\n\nʙᴏᴛ ɪs ᴡᴏʀᴋɪɴɢ ᴏɴ ɢʀᴏᴜᴘ....✅</b>", disable_web_page_preview=True)
        return
 
    # msg = await message.reply_text(f"<b>Searching for your request...</b>", reply_to_message_id=message.id)
    
    files, _, _ = await get_search_results(message.text.lower(), offset=0, filter=True)
    if not files:
        google = "https://google.com/search?q="
        reply_markup = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔍 Check Your Spelling", url=f"{google}{quote(message.text.lower())}%20movie")],
            [InlineKeyboardButton("🗓 Check Release Date", url=f"{google}{quote(message.text.lower())}%20release%20date")]
        ])
        await message.reply(
            text=script.NO_MOVIE,
            reply_markup=reply_markup,
        )
        return      
    
    filter = None
    try:
        if premium_status is True:
            if await db.check_expired_users(user_id):
                await message.reply(f"<b>Your premium subscription has been expired. Please <a href=https://t.me/{temp.U_NAME}?start=upgrade>renew</a> your subscription to continue using premium.</b>", disable_web_page_preview=True)
                return
        #     if files_counts >= 100:
        #         await msg.edit(f"<b>Your account has been locked due to spamming/misuse, And it'll be unlocked after {time_difference} hours.</b>")
        #         return
        # else:
        #     if user_timestamps:
        #         current_time = int(time.time())
        #         time_diff = current_time - user_timestamps
        #         if time_diff < SLOW_MODE_DELAY:
        #             remaining_time = SLOW_MODE_DELAY - time_diff
        #             while remaining_time > 0:
        #                 await msg.edit(f"<b>Please wait for {remaining_time} seconds before sending another request.</b>")
        #                 await asyncio.sleep(1)
        #                 remaining_time = max(0, SLOW_MODE_DELAY - int(time.time()) + user_timestamps)
        #             await message.delete()
        #             await msg.delete()
        #             return

        #     if files_counts >= 15:
        #         await msg.edit(
        #             f"<b>You have reached your daily Limit. Please try after {time_difference} hours, or  <a href=https://t.me/{temp.U_NAME}?start=upgrade>upgrade to premium</a> for unlimited request.</b>",
        #             disable_web_page_preview=True)
        #         return

        text, button = await auto_filter(client, message)
        filter = await message.reply(text=f"<b>{text}</b>", reply_markup=button, disable_web_page_preview=True)

    # except Exception as e:
    #     logger.error(e)
    #     w = await message.reply(f"<b>Opps! Something went wrong.</b>")
    #     await asyncio.sleep(5)
    #     await w.delete()

    finally:
        if filter:
            await asyncio.sleep(600)
            await filter.delete()
            await message.delete()

@Client.on_message(filters.group & filters.text & filters.incoming)
async def public_group_filter(client, message):

    if message.text.startswith(("/", "@")) or not await mdb.get_configuration_value("group_filter"):
        return
    
    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)

    await mdb.update_top_messages(message.from_user.id, message.text)
    
    filter = None
    if message.chat.id in AUTH_GROUPS:
        try:
            text, button = await auto_filter(client, message)
            filter = await message.reply(text=f"<b>{text}</b>", reply_markup=button, disable_web_page_preview=True)
        except Exception as e:
            logger.error(e) 

        finally:
            if filter:
                await asyncio.sleep(600)
                await message.delete()
                await filter.delete()
    else:
        try:
            text, button = await auto_filter(client, message)
            filter = await message.reply(text=f"<b>{text}</b>", reply_markup=button, disable_web_page_preview=True)
        except Exception as e:
            logger.error(e)      

@Client.on_callback_query(filters.regex(r"^spolling"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer("Not For You", show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer("You are clicking on an old button which is expired.", show_alert=True)
    movie = movies[(int(movie_))]
    await query.answer('Checking for Movie in database...')
    files, offset, total_results = await get_search_results(movie, offset=0, filter=True)
    if files:
        k = (movie, files, offset, total_results)
        text, button = await auto_filter(bot, query, k)
        await query.message.edit(text, reply_markup=button, disable_web_page_preview=True)
    else:
        k = await query.message.edit("<b>Lᴏᴏᴋ's Lɪᴋᴇ Yᴏᴜʀ Mᴏᴠɪᴇ Nᴀᴍᴇ Is Wʀᴏɴɢ....⚠️\nPʟᴇᴀsᴇ Sᴇɴᴅ Tʀᴜᴇ Nᴀᴍᴇ....✅</b>")
        await asyncio.sleep(30)
        await k.delete()


async def advantage_spell_chok(msg):
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # plis contribute some common words
    query = query.strip() + " movie"
    g_s = await search_gagala(query)
    g_s += await search_gagala(msg.text)
    gs_parsed = []
    if not g_s:
        k = await msg.reply(script.NO_MOVIE)
        await asyncio.sleep(150)
        await k.delete()
        return
    regex = re.compile(r".*(imdb|wikipedia).*", re.IGNORECASE)  # look for imdb / wiki results
    gs = list(filter(regex.match, g_s))
    gs_parsed = [re.sub(
        r'\b(\-([a-zA-Z-\s])\-\simdb|(\-\s)?imdb|(\-\s)?wikipedia|\(|\)|\-|reviews|full|all|episode(s)?|film|movie|series)',
        '', i, flags=re.IGNORECASE) for i in gs]
    if not gs_parsed:
        reg = re.compile(r"watch(\s[a-zA-Z0-9_\s\-\(\)]*)*\|.*",
                         re.IGNORECASE)  # match something like Watch Niram | Amazon Prime
        for mv in g_s:
            match = reg.match(mv)
            if match:
                gs_parsed.append(match.group(1))
    user = msg.from_user.id if msg.from_user else 0
    movielist = []
    gs_parsed = list(dict.fromkeys(gs_parsed))  # removing duplicates https://stackoverflow.com/a/7961425
    if len(gs_parsed) > 3:
        gs_parsed = gs_parsed[:3]
    movielist += [(re.sub(r'(\-|\(|\)|_)', '', i, flags=re.IGNORECASE)).strip() for i in gs_parsed]
    movielist = list(dict.fromkeys(movielist))  # removing duplicates
    if not movielist:
        k = await msg.reply(script.NO_MOVIE)
        await asyncio.sleep(150)
        await k.delete()
        return
    SPELL_CHECK[msg.id] = movielist
    btn = [[
        InlineKeyboardButton(
            text=movie.strip(),
            callback_data=f"spolling#{user}#{k}",
        )
    ] for k, movie in enumerate(movielist)]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spolling#{user}#close_spellcheck')])
    m = await msg.reply(f"<b>Did you mean any one of these ?</b>",
                    reply_markup=InlineKeyboardMarkup(btn))
    
async def CHOKLE(msg):
    d = await msg.reply_text(text=script.NO_MOVIE)
    await asyncio.sleep(150)
    await d.delete()
    
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    _, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(f"You can't access someone else's request.", show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer("You are using one of my old messages, please send the request again.", show_alert=True)
        return

    files, n_offset, total = await get_search_results(search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    # Construct a text message with hyperlinks
    is_all_time_ads = await mdb.get_configuration_value("all_time_ad")    
    search_results_text = []
    for file in files:
        user_id = query.from_user.id
        user_id_bytes = str(user_id).encode('utf-8')
        urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8')
        fileslink = f"https://telegram.me/{temp.U_NAME}?start={temp.U_NAME}-{urlsafe_encoded_user_id}_{file.file_id}"
        
        if is_all_time_ads:
            fileslink = await shortlink(fileslink)
            
        escaped_file_name = await escape_markdown(await replace_blacklist(file.file_name, script.BLACKLIST))
        file_link = f"📕 [{get_size(file.file_size)} | {escaped_file_name}]({fileslink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []
    
    if 0 < offset <= 10:
        off_set = 0
    elif offset == 0:
        off_set = None
    else:
        off_set = offset - 10
    if n_offset == 0:
        btn.append(
            [InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
             InlineKeyboardButton(f"📃 Pages {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}",
                                  callback_data="pages")]
        )
    elif off_set is None:
        btn.append(
            [InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
             InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")])
    else:
        btn.append(
            [
                InlineKeyboardButton("⏪ BACK", callback_data=f"next_{req}_{key}_{off_set}"),
                InlineKeyboardButton(f"🗓 {math.ceil(int(offset) / 10) + 1} / {math.ceil(total / 10)}", callback_data="pages"),
                InlineKeyboardButton("NEXT ⏩", callback_data=f"next_{req}_{key}_{n_offset}")
            ],
        )
    try:
         await query.edit_message_text(
            text=f"<b>{search_results_text}</b>",
            disable_web_page_preview=True,
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()
    
    
async def auto_filter(_, msg, spoll=False):
    if not spoll:
        message = msg
        if message.text.startswith("/"):
            return
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if 2 < len(message.text) < 100:
            search = message.text
            find = search.split(" ")
            search = ""
            removes = ["in","upload", "series", "full", "horror", "thriller", "mystery", "print", "file", "send", "chahiye", "chiye", "movi", "movie", "bhejo", "dijiye", "jaldi", "hd", "bollywood", "hollywood", "south", "karo"]
            for x in find:
                if x in removes:
                    continue
                else:
                    search = search + x + " "
            files, offset, total_results = await get_search_results(search.lower(), offset=0, filter=True)
            if not files:
                # if await mdb.get_configuration_value("spoll_check"):
                return await CHOKLE(msg)
                # else:
                #     return
        else:
            return
    else:
        message = msg.message.reply_to_message
        search, files, offset, total_results = spoll
        
    # Construct a text message with hyperlinks
    is_all_time_ads = await mdb.get_configuration_value("all_time_ad")
    is_user_premium = await db.is_premium_status(message.from_user.id)
    search_results_text = []
    for file in files:
        user_id = message.from_user.id
        user_id_bytes = str(user_id).encode('utf-8')
        urlsafe_encoded_user_id = base64.urlsafe_b64encode(user_id_bytes).decode('utf-8')
        fileslink = f"https://telegram.me/{temp.U_NAME}?start={temp.U_NAME}-{urlsafe_encoded_user_id}_{file.file_id}"
        
        if is_all_time_ads and not is_user_premium:
            fileslink = await shortlink(fileslink)
            
        escaped_file_name = await escape_markdown(await replace_blacklist(file.file_name, script.BLACKLIST))
        file_link = f"📕 [{get_size(file.file_size)} | {escaped_file_name}]({fileslink})"
        search_results_text.append(file_link)

    search_results_text = "\n\n".join(search_results_text)

    btn = []   
    # btn.append([
    #         InlineKeyboardButton("🪙 Upgrade", callback_data="upgrade_call"),
    #         InlineKeyboardButton("🔗 Refer", callback_data="refer_call")
    #     ])
    ads, ads_name, _ = await mdb.get_advirtisment()
    ads, ads_name, _ = await mdb.get_advirtisment()
    if ads is not None and ads_name is not None:
        btn.append([InlineKeyboardButton(text=f"{ads_name}", url=f"https://t.me/{temp.U_NAME}?start=ads")])

    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        btn.append(
            [InlineKeyboardButton(text=f"🗓 1/{math.ceil(int(total_results) / 10)}", callback_data="pages"),
             InlineKeyboardButton(text="NEXT ⏩", callback_data=f"next_{req}_{key}_{offset}")]
        )
    else:
        btn.append(
            [InlineKeyboardButton(text="🗓 1/1", callback_data="pages")]
        )
    # cap = f"Here is what I found for your request ~ {search}"
    # add timestamp to database for floodwait
    await db.update_value(message.from_user.id, "timestamps", int(time.time()))
    return f"{search_results_text}", InlineKeyboardMarkup(btn)

async def get_link(client, message):
    local_text = message.text
    mkv = local_text.replace(" ", "-").replace(".", " ").replace(",", " ").replace(":", " ").replace(":", " ").replace("'", " ").replace("_", " ")
    # movie_name = local_text[1].replace(" ", "-")

    link = f"https://telegram.me/{temp.U_NAME}?start=search-{mkv}"
    
    k = await message.reply_text(
        text=f"<a href={link}>**Here Is The File List \nFor Your Request 📩**</a>",
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton(text="📂 Get Files", url=f"{link}")]]
        )
    )
    await asyncio.sleep(150)
    await k.delete()

async def escape_markdown(text):
    # List of special characters that need to be escaped in markdown
    markdown_chars = ['*', '_', '#', '[', ']', '(', ')', '`', '>', '+', '-', '.', '!']
    for char in markdown_chars:
        text = text.replace(char, ' ' + char)
    return text

@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    if query.data == "close_data":
        await query.message.delete()
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        _, btn, alerts, _ = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)

    if query.data.startswith("checksub"):
        if FORCESUB_CHANNEL and not await is_subscribed(client, query):
            await query.answer(f"Please join my channel first after that click on 'Try Again'", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exist.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        await client.send_cached_media(
            chat_id=query.from_user.id,
            file_id=file_id,
            caption=f"{await replace_blacklist(f_caption, script.BLACKLIST)}",
        )
        # del_msg = await client.send_message(
        #     text=f"<b>File will be deleted in 10 mins. Save or forward immediately.<b>",
        #     chat_id=query.from_user.id,
        #     reply_to_message_id=md_id.id
        #     )
        # await asyncio.sleep(WAIT_TIME or 600)
        # await md_id.delete()
        # await del_msg.edit("__⊘ This message was deleted__")
        
    elif query.data == "pages":
        qoute = await fetch_quote_content()
        await query.answer(f"{qoute}", show_alert=True)
    elif query.data == "home":
        buttons = [[
                    # InlineKeyboardButton('Refer', callback_data="refer"),
                    # InlineKeyboardButton('Premium', callback_data="upgrd")
                    # ],[
                    InlineKeyboardButton('⚠️ ғᴇᴀᴛᴜʀᴇ', callback_data='help'),
                    InlineKeyboardButton('🌿 ᴀʙᴏᴜᴛ', callback_data='about')
                    ],[
                    InlineKeyboardButton('📕 sᴜᴘᴘᴏʀᴛ', web_app=WebAppInfo(url="https://qr-code-bob-files.vercel.app")),
                    InlineKeyboardButton('📩 ʀᴇᴏ̨ᴜᴇsᴛ', callback_data="request")
                  ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit(
        text=script.START_TXT.format(query.from_user.mention, temp.B_NAME),
        reply_markup=reply_markup,
        disable_web_page_preview=True,
        )
        if not await db.is_user_exist(query.from_user.id):
            await db.add_user(
                query.from_user.id,
                query.from_user.first_name
                )
        
    elif query.data == "about":
        buttons = [[InlineKeyboardButton('🏠 Home', callback_data="home")]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            disable_web_page_preview=True,
            reply_markup=reply_markup
        )
        
    elif query.data == "help":
        await query.answer("Chala Ja BSDK", show_alert=True)
        

    elif query.data.startswith("not_available"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 Support Here 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने " {movie} " का report भेजा है वो\nमूवी हमें नई मिला...🤒\n\n━━━━━━━━━━━━━━━━━━\n\nʏᴏᴜʀ ʀᴇǫᴜɪʀᴇᴅ " {movie} " ɪꜱ\nɴᴏᴛ ᴀᴠᴀɪʟᴀʙʟᴇ....</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Nᴏᴛ Aᴠᴀɪʟᴀʙʟᴇ 😒.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
    elif query.data.startswith("already_available"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐞𝐫𝐞 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने जो " {movie} " का रिपोर्ट भेजा है\nवो मूवी पहले से ही ग्रुप में हे...✅\n\nअगर नई मिल रहा है तो मूवी का\nरिलीस year भी लिखे....😘\n\nPushpa 2021\nChhichhore 2019\nSaalar 2024\n\n━━━━━━━━━━━━━━━━━━\n\nʏᴏᴜʀ ʀᴇǫᴜᴇꜱᴛᴇᴅ " {movie} " ɪꜱ ᴀʟʀᴇᴀᴅʏ\nᴀᴠᴀɪʟᴀʙʟᴇ ɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ....✅\nɪꜰ ʙᴏᴛ ɪꜱ ɴᴏᴛ ꜱᴇɴᴅɪɴɢ....🫠\nᴛʜᴇɴ ᴛʏᴘᴇ ᴀꜱʟᴏ ᴍᴏᴠɪᴇ\nʀᴇʟᴇᴀꜱᴇ ʏᴇᴀʀ....😘\n\nPushpa 2021\nChhichhore 2019\nSaalar 2024</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Already Aᴠᴀɪʟᴀʙʟᴇ 🤩.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
    elif query.data.startswith("uploaded"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐞𝐫𝐞 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने " {movie} " का रिपोर्ट भेजा था वो\nमूवी हमने ग्रुप में डाल दिया है....✅\n\nग्रुप में वापस नाम लिखने पर आपको\nमूवी मिल जाएगा....🎉\n\n━━━━━━━━━━━━━━━━━━\n\nʏᴏᴜʀ " {movie} " ʜᴀꜱ ʙᴇᴇɴ ᴀᴅᴅᴇᴅ\nɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ ....🎉\n\nᴘzzzz ʀᴇǫᴜᴇꜱᴛ ᴀɢᴀɪɴ & ɢᴇᴛ....✅</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Uᴘʟᴏᴀᴅᴇᴅ 🎊.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
    elif query.data.startswith("not_release"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐞𝐫𝐞 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने जो " {movie} " का रिपोर्ट भेजा है\nवो अभी रिलीस नई हुआ है...📅\n\nजब रिलीस होगा तब ग्रुप में\nमिल जाएगा....✅\n\n━━━━━━━━━━━━━━━━━━\n\nʏᴏᴜʀ ʀᴇǫᴜɪʀᴇᴅ " {movie} "\nɪꜱ ɴᴏᴛ ʀᴇʟᴇᴀꜱᴇᴅ....😅\n\nᴡʜᴇɴ ʀᴇʟᴇᴀꜱᴇ ᴛʜᴇɴ ᴡᴇ ᴡɪʟʟ\nᴀʟꜱᴏ ᴜᴘʟᴏᴅ ɪɴ ᴏᴜʀ ɢʀᴏᴜᴘ.....🎉</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Not Release 🙅.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
    elif query.data.startswith("spelling_error"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐞𝐫𝐞 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने जो " {movie} " का रिपोर्ट भेजा है\nउस में स्प्रेलिंग गलत है....😅\n\nकृपया गूगल से स्पेलिंग कॉपी\nकर के लिखे....🙏\n\n━━━━━━━━━━━━━━━━━━\n\nᴄʜᴀᴄᴋ ʏᴏᴜʀ ꜱᴘᴇʟʟɪɴɢ....👀\n\nᴘʟᴢᴢᴢ ᴄᴏᴘʏ ꜱᴘᴇʟʟɪɴɢ ꜰʀᴏᴍ\nɢᴏᴏɢʟᴇ & ᴡʀɪᴛᴇ....👀</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Sᴘᴇʟʟɪɴɢ Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return
    elif query.data.startswith("series"):
        _, user_id, movie = query.data.split(":")
        try:
            safari = [[
                    InlineKeyboardButton(text=f"❌ close ❌", callback_data = "close_data")
                    ]]
            thh = [[
                    InlineKeyboardButton(text=f"🔥 𝐑𝐞𝐪𝐮𝐞𝐬𝐭 𝐇𝐞𝐫𝐞 🔥", url=REQUEST_GROUP)
            ]]
            reply_markup = InlineKeyboardMarkup(safari)
            await client.send_message(int(user_id), f'<b>आपने जो " {movie} " सीरीज का रिपोर्ट\nकिया है उस का नाम आपने गलत\nतरीके से लिखा है....🥱\nइस तरह से लिखे....👇\n\nMoney Heist S01\nKota Factory S01E05\nMoney Heist S03E04\n\n━━━━━━━━━━━━━━━━━━\n\nʏᴏᴜ ʜᴀᴠᴇ ᴡʀɪᴛᴛᴇɴ ɴᴀᴍᴇ\nᴏꜰ " {movie} " ꜱᴇʀɪᴇꜱ.....👀\nʏᴏᴜ ʜᴀᴠᴇ ʀᴇǫᴜɪʀᴇᴅ ᴡʀᴏɴɢʟʏ...🥱\nMoney Heist S01\nKota Factory S01E05\nMoney Heist S03E04</b>', reply_markup=InlineKeyboardMarkup(thh))
            msg=await query.edit_message_text(text=f"Mᴇꜱꜱᴀɢᴇ Sᴇɴᴅ Sᴜᴄᴄᴇꜱꜱғᴜʟʟʏ ✅\n\n⏳ꜱᴛᴀᴛᴜꜱ : Series Eʀʀᴏʀ 🕵️.\n🪪ᴜꜱᴇʀɪᴅ : tg://openmessage?user_id={user_id}\n🎞ᴄᴏɴᴛᴇɴᴛ : `{movie}`", reply_markup=InlineKeyboardMarkup(safari))
            await asyncio.sleep(3)
            await msg.delete()
        except Exception as e:
            print(e)  # print the error message
            await query.answer(f"☣something went wrong\n\n{e}", show_alert=True)
            return



    elif query.data == "close_data":
        await query.message.delete()
    elif query.data == "request":
        buttons = [[
                    InlineKeyboardButton('📽️ Request Group', url=f"{REQUEST_GROUP}"),
                    InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        await query.message.edit(
        text=script.REQM,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )                
    elif query.data == "upgrd":
        buttons = [[
                    InlineKeyboardButton('💳 Pay', web_app=WebAppInfo(url="https://qr-code-bob-files.vercel.app/")),
                    InlineKeyboardButton('💫 Confirm', callback_data="confirm")
                ]]
        tnc= f"<a href=https://t.me/{temp.U_NAME}?start=terms>T&C apply</a>"
        await query.message.edit(
        text=script.UPGRD_TXT.format(tnc),
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )
       
    elif query.data == "confirm":
        buttons = [[
                    InlineKeyboardButton('📣 Help', url="https://t.me/ASSAULTER_SHIV"),
                    InlineKeyboardButton('🏠 Home', callback_data="home"),
                ]]
        await query.message.edit(
        text=script.CNFRM_TEXT,
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True,
        )

    elif query.data == "checkjoin":
        forcesub = await mdb.get_configuration_value("forcesub")
        if FORCESUB_CHANNEL and forcesub and not await is_subscribed(client, query):
            await query.answer("Please join in my channel dude!", show_alert=True)
        else:
            await query.answer("Thanks for joining, Now you can continue searching", show_alert=True)
            await query.message.delete()

    elif query.data == "refer":
        user_id = query.from_user.id
        referral_points = await db.fetch_value(user_id, "referral")
        refferal_link = f"https://t.me/{temp.U_NAME}?start=ReferID-{user_id}"
        buttons = [[
                    InlineKeyboardButton('🎐 Invite', url=f"https://telegram.me/share/url?url={refferal_link}&text=Hello%21%20Experience%20a%20bot%20that%20offers%20a%20vast%20library%20of%20unlimited%20movies%20and%20series.%20%F0%9F%98%83"),
                    InlineKeyboardButton(f"🟢 {referral_points}", callback_data="refer_point"),
                    InlineKeyboardButton('◀️ Back', callback_data="home")
                ]]
        await query.message.edit(
            text=script.REFFERAL_TEXT.format(refferal_link),
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )

    elif query.data == "refer_point":
        user_id = query.from_user.id
        referral_points = await db.fetch_value(user_id, "referral")
        await query.answer(f"You have {referral_points} refferal points.", show_alert=True
        )
    
    elif query.data == "upgrade_call":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=upgrade")
        return
    
    elif query.data == "refer_call":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=refer")
        return
    
    elif query.data == "terms":
        buttons = [[
                    InlineKeyboardButton("✅ Accept Terms", callback_data="home"),
                ]]
        await query.message.edit(
            text=script.TERMS,
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif query.data == "why_verify":
        buttons = [[
                    InlineKeyboardButton("⛔ Close", callback_data="close_data"),
                ]]
        await query.message.edit(
            text=f"<b>🍁 We put in a lot of effort to provide you with the latest movies and series, and keeping our bots and servers running smoothly requires effort, time and cost. That's why we kindly ask you to 'Verify,' which helps us generate revenue to keep offering these services. Your support is greatly appreciated.</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
            )
        return

    # Function to delete unwanted files
    elif query.data == "delback":
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

        await query.message.edit(
            text="<b>Select The Type Of Files You Want To Delete..?</b>",
            reply_markup=InlineKeyboardMarkup(btn)
        )
        
    elif query.data in ["predvd", "camrip", "predvdrip", "hdcam", "hdcams", "print", "hdts", "sample", "hdtc"]:
        buttons = [[
            InlineKeyboardButton("10", callback_data=f"dlt#10_{query.data}")
            ],[
            InlineKeyboardButton("100", callback_data=f"dlt#100_{query.data}")
            ],[
            InlineKeyboardButton("1000", callback_data=f"dlt#1000_{query.data}")
            ],[
            InlineKeyboardButton('⛔️ Close', callback_data="close_data"),
            InlineKeyboardButton('◀️ Back', callback_data="delback")
        ]]
        await query.message.edit(
            text=f"<b>How Many {query.data.upper()} Files You Want To Delete?</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True
        )
    
    elif query.data.startswith("dlt#"):
        limit, file_type = query.data.split("#")[1].split("_")
        buttons = [[
            InlineKeyboardButton('Hell No', callback_data=f"confirm_no")
            ],[           
            InlineKeyboardButton('Yes, Delete', callback_data=f"confirm_yes#{limit}_{file_type}")
            ],[
            InlineKeyboardButton('⛔️ Close', callback_data="close_data")
        ]]
        await query.message.edit(
            text=f"<b>Are You Sure To Delete {limit} {file_type.upper()} Files?</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif query.data.startswith("confirm_yes#"):
        limits, file_type = query.data.split("#")[1].split("_")
        limit = int(limits)
        await delete_files(query, limit, file_type)

    elif query.data == "confirm_no":
        await query.message.edit(text=f"<b>Deletion canceled.</b>", reply_markup=None)

    # Function for getting the trending search results
    elif query.data == "trending":
        await query.answer(url=f"https://t.me/{temp.U_NAME}?start=trending")
        return

    # generate redeem code
    elif query.data.startswith("redeem"):
        buttons = [[
            InlineKeyboardButton("1 Month", callback_data="Reedem#30")
            ],[
            InlineKeyboardButton("6 Months", callback_data="Reedem#180")
            ],[
            InlineKeyboardButton("12 Months", callback_data="Reedem#365")
            ]]
        await query.message.edit(
            f"<b>Choose the duration</b>",
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )
    elif query.data.startswith("Reedem#"):
        duration = query.data.split("#")[1]
        buttons = [[
            InlineKeyboardButton("1 Redeem Code", callback_data=f"license#{duration}#1")
            ],[
            InlineKeyboardButton("5 Redeem Codes", callback_data=f"license#{duration}#5")
            ],[
            InlineKeyboardButton("10 Redeem Codes", callback_data=f"license#{duration}#10")
            ]]  
        await query.message.edit(f"<b>How many redeem codes you want?</b>", 
            reply_markup=InlineKeyboardMarkup(buttons),
            disable_web_page_preview=True,
        )    
    elif query.data.startswith("license#"):
        duration, count = query.data.split("#")[1:]
        encoded_duration = base64.b64encode(str(duration).zfill(3).encode()).decode('utf-8').rstrip('=')

        codes_generated = []
        for _ in range(int(count)):
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{REDEEM_BASE_URL}/?access_key={ACCESS_KEY}&action=generate&days=90") as resp:
                    if resp.status == 200:
                        json_response = await resp.json()
                        license_code = f"{json_response.get('license_code')[:10]}{encoded_duration}{json_response.get('license_code')[10:]}"
                        codes_generated.append(license_code)
                    else:
                        await query.answer(f"Error generating license code.{resp.status}", show_alert=True)
                        return
                
        codes_str = "\n".join(f"`{code}`" for code in codes_generated)
        await query.message.edit(f"<b>Redeem codes:</b>\n\n{codes_str}")

    #maintainance
    elif query.data == "maintenance":
        await toggle_config(query, "maintenance_mode", "Maintenance mode")
    elif query.data == "autoapprove":
        await toggle_config(query, "auto_accept", "Auto approve")
    elif query.data == "private_filter":
        await toggle_config(query, "private_filter", "Private filter")
    elif query.data == "group_filter":
        await toggle_config(query, "group_filter", "Group filter")
    elif query.data == "terms_and_condition":
        await toggle_config(query, "terms", "Terms&Condition")
    elif query.data == "spoll_check":
        await toggle_config(query, "spoll_check", "Spell Check")
    elif query.data == "force_subs":
        await toggle_config(query, "forcesub", "Force Subscribe")
    elif query.data == "glob_link_acess":
        await toggle_config(query, "global_link_access", "Link access for all")
    elif query.data == "all_time_ad_callback":
        await toggle_config(query, "all_time_ad", "All Time Ads")

    elif query.data == "others":
        button=[
            [InlineKeyboardButton("Private Filter ⚪️" if await mdb.get_configuration_value("private_filter") else "Private Filter", callback_data="private_filter")],
            [InlineKeyboardButton("Group Filter ⚪️" if await mdb.get_configuration_value("group_filter") else "Group Filter", callback_data="group_filter")],
            [InlineKeyboardButton("Maintainace ⚪️" if await mdb.get_configuration_value("maintenance_mode") else "Maintainace", callback_data="maintenance")],
            ]
        reply_markup = InlineKeyboardMarkup(button)
        await query.message.edit(
            text=f"<b>Choose the option</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        )      
    # Shortner button
    elif query.data == "shortner":
        shortnr = await mdb.get_configuration_value("shortner")
        buttons = [[
            InlineKeyboardButton("Shareus ⚪️" if shortnr == "shareus" else "Shareus", callback_data="shareus"),
            InlineKeyboardButton("GPLinks ⚪️" if shortnr == "gplinks" else "GPLinks", callback_data="gplinks"),
            ],[
            InlineKeyboardButton("UrlShare ⚪️" if shortnr == "urlshare" else "UrlShare", callback_data="urlshare"),
            InlineKeyboardButton("AdLinkfly ⚪️" if shortnr == "adlinkfly" else "AdLinkFly", callback_data="adlinkfly"),
            ],[
            InlineKeyboardButton("RunUrl ⚪️" if shortnr == "runurl" else "RunUrl", callback_data="runurl"),
            InlineKeyboardButton("AdLinkfly ⚪️" if shortnr == "adlinkfly" else "AdLinkFly", callback_data="adlinkfly"),
            ],[
            InlineKeyboardButton("Thh ⚪️" if shortnr == "thh" else "Thh", callback_data="thh"),
            # InlineKeyboardButton("AdLinkfly ⚪️" if shortnr == "adlinkfly" else "AdLinkFly", callback_data="adlinkfly"),
            ],[
            InlineKeyboardButton("No Shortner ⚪️" if shortnr == "no_shortner" else "No Shortner", callback_data="no_shortner"),
            ],[
            InlineKeyboardButton("⛔️ Close", callback_data="close_data")
            ]]
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit(
            text=f"<b>Choose the shortner</b>",
            reply_markup=reply_markup,
            disable_web_page_preview=True,
        ) 
    elif query.data == "shareus":
        await set_shortner(query, "shareus")
    elif query.data == "gplinks":
        await set_shortner(query, "gplinks")
    elif query.data == "adlinkfly":
        await set_shortner(query, "adlinkfly")
    elif query.data == "urlshare":
        await set_shortner(query, "urlshare")
    elif query.data == "runurl":
        await set_shortner(query, "runurl")
    elif query.data == "thh":
        await set_shortner(query, "thh")
    elif query.data == "no_shortner":
        await set_shortner(query, "no_shortner")      

    await query.answer('Welcome TO The Happy Hour 🥂')

async def set_shortner(query, shortner):
    await mdb.update_configuration("shortner", shortner)
    await query.message.edit(f"<b>{shortner} shortner enabled.</b>", reply_markup=None)

async def toggle_config(query, config_key, message):
    config = await mdb.get_configuration_value(config_key)
    if config is True:
        await mdb.update_configuration(config_key, False)
        await query.message.edit(f"<b>{message} disabled.</b>", reply_markup=None)
    else:
        await mdb.update_configuration(config_key, True)
        await query.message.edit(f"<b>{message} enabled.</b>", reply_markup=None)


async def delete_files(query, limit, file_type):
    k = await query.message.edit(text=f"Deleting <b>{file_type.upper()}</b> files...", reply_markup=None)
    files, _, _ = await get_search_results(file_type.lower(), max_results=limit, offset=0)
    deleted = 0

    for file in files:
        file_ids = file.file_id
        result = await Media.collection.delete_one({'_id': file_ids})

        if result.deleted_count:
            logger.info(f'{file_type.capitalize()} File Found! Successfully deleted from database.')

        deleted += 1

    deleted = str(deleted)
    await k.edit_text(text=f"<b>Successfully deleted {deleted} {file_type.upper()} files.</b>")  
