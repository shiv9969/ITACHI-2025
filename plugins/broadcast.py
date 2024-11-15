from pyrogram import Client, filters
import datetime, asyncio, time, logging
from database.users_chats_db import db
from info import ADMINS
from pyrogram.errors import FloodWait, InputUserDeactivated, UserIsBlocked, PeerIdInvalid

@Client.on_message(filters.command("broadcast") & filters.user(ADMINS) & filters.reply)
async def broadcasting(bot, message):
    users_cursor = await db.get_all_users()
    users = await users_cursor.to_list(length=None)  # Convert the cursor to a list
    b_msg = message.reply_to_message
    sts = await message.reply_text(
        text='Broadcasting your messages...'
    )
    start_time = time.time()
    total_users = await db.total_users_count()
    done = 0
    blocked = 0
    deleted = 0
    failed =0

    success = 0
    users_chunks = [users[i:i + 10] for i in range(0, len(users), 10)]  # Split users into chunks of 10
    for users_chunk in users_chunks:
        tasks = []
        for user in users_chunk:
            tasks.append(broadcast_func(user, b_msg))  # Create a new task for each user
        results = await asyncio.gather(*tasks)  # Run the tasks concurrently
        for result in results:
            s, b, d, f, done_increment = result
            success += s
            blocked += b
            deleted += d
            failed += f
            done += done_increment
        # await asyncio.sleep(.1)
        if not done % 50:
            await sts.edit(f"Broadcast in progress:\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")    
    time_taken = datetime.timedelta(seconds=int(time.time()-start_time))
    await sts.edit(f"Broadcast Completed:\nCompleted in {time_taken} seconds.\n\nTotal Users {total_users}\nCompleted: {done} / {total_users}\nSuccess: {success}\nBlocked: {blocked}\nDeleted: {deleted}")

async def broadcast_func(user, b_msg):
    success, blocked, deleted, failed, done = 0, 0, 0, 0, 0
    pti, sh = await broadcast_messages(int(user['id']), b_msg)
    if pti:
        success = 1
    elif pti == False:
        if sh == "Blocked":
            blocked=1
        elif sh == "Deleted":
            deleted = 1
        elif sh == "Error":
            failed = 1
    done = 1
    return success, blocked, deleted, failed, done

async def broadcast_messages(user_id, message):
    try:
        await message.copy(chat_id=user_id)
        return True, "Success"
    except FloodWait as e:
        await asyncio.sleep(e.x)
        return await broadcast_messages(user_id, message)
    except InputUserDeactivated:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id}-Removed from Database, since deleted account.")
        return False, "Deleted"
    except UserIsBlocked:
        logging.info(f"{user_id} -Blocked the bot.")
        return False, "Blocked"
    except PeerIdInvalid:
        await db.delete_user(int(user_id))
        logging.info(f"{user_id} - PeerIdInvalid")
        return False, "Error"
    except Exception as e:
        return False, "Error"
