from pyrogram import Client, filters
from database.ia_filterdb import get_file_details, get_all_file_ids, Media
from info import FORWARD_CHANNEL, ADMINS
import asyncio, logging
from utils import replace_blacklist
from Script import script
from pyrogram.errors import BadRequest, FloodWait

# Set up logging
logging.basicConfig(level=logging.ERROR)

lock = asyncio.Lock()

async def forward_file(client, file_id, caption):
    try:
        await client.send_cached_media(
            chat_id=FORWARD_CHANNEL,
            file_id=file_id,
            caption=caption,
        )
        return True
    except Exception as e:
        logging.error(f"Error forwarding file: {e}")
        return False

async def get_files_from_db(client, message, cancel_forwarding):
    m = await message.reply_text(text=f"**Wait...It'll take a decade to process**")
    
    total_files = await Media.count_documents()
    total = 0
    failed = 0
    async for file in get_all_file_ids():
        if cancel_forwarding:
            await m.edit("**File forwarding process has been canceled.**")
            return

        file_id = file
        file_details = await get_file_details(file_id)
        file_info = file_details[0]
        cap = file_info.caption or file_info.file_name
        caption = f"<code>{await replace_blacklist(cap, script.BLACKLIST)}</code>"
        try:
            success = await forward_file(client, file_id, caption)
            if success:
                total += 1
                await m.edit(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
        except BadRequest as bad:
                failed += 1
                await m.edit(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
                logging.error(f"BadRequest: {bad}")
                await asyncio.sleep(1)

        except FloodWait as e:
            logging.warning(f"FloodWait: Waiting for {e.x} seconds.")
            await asyncio.sleep(e.x)

    await m.edit(f"**Successfully forwarded {total} files from the database.**")

@Client.on_message(filters.command("copydb") & filters.user(ADMINS))
async def copydb_command(client, message):
    if lock.locked():
        await message.reply('Wait until previous process complete.')
    else:
        with lock:
            cancel_forwarding = False
            if len(message.command) > 1:
                sub_command = message.command[1].lower()
                if sub_command == "cancel":
                    cancel_forwarding = True
                    await message.reply("**File forwarding canceled.**")
                    return
            try:
                await get_files_from_db(client, message, cancel_forwarding)
            except Exception as e:
                await message.reply(f"**Error: {e}**")


async def forward_files_in_sequence(client, sequence_number):
    total_files = await Media.count_documents()
    if sequence_number > total_files:
        return f"Error: Sequence number {sequence_number} is greater than the total number of files {total_files}."
    
    total = 0
    failed = 0
    file_ids = [file async for file in get_all_file_ids()]
    file_id = file_ids[sequence_number - 1]
    file_details = await get_file_details(file_id)
    file_info = file_details[0]
    cap = file_info.caption or file_info.file_name
    caption = f"<code>{await replace_blacklist(cap, script.BLACKLIST)}</code>"
    try:
        success = await forward_file(client, file_id, caption)
        if success:
            total += 1
            print(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
    except BadRequest as bad:
        failed += 1
        print(f"**Success** - {total}\n**Total** - {total_files}\n**Failed** - {failed}")
        logging.error(f"BadRequest: {bad}")
        await asyncio.sleep(1)
    except FloodWait as e:
        logging.warning(f"FloodWait: Waiting for {e.x} seconds.")
        await asyncio.sleep(e.x)
    

@Client.on_message(filters.command("copyfrom"))
async def copyfrom(client, message):
    if len(message.command) > 1:
        sequence_number = message.command[1]
        if not sequence_number.isdigit() or int(sequence_number) <= 0:
            await message.reply("**Error: Please provide a positive integer as the sequence number.**")
            return
        sequence_number = int(sequence_number)
        try:
            await forward_files_in_sequence(client, sequence_number)
        except Exception as e:
            await message.reply(f"**Error: {e}**")
    else:
        await message.reply("**Error: Please provide a sequence number.**")