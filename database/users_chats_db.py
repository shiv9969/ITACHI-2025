import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI
from datetime import datetime, timedelta


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.request = self.db.requests
        self.stream_link = self.db.stream_link
        
        
    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            Premium=False, 
            premium_expiry=None, 
            purchase_date=None, 
            timestamps=0,
            user_joined=False, 
            files_count=0,
            verified=False,
            lifetime_files=0, 
            referral=0,
            last_reset=datetime.now().strftime("%Y-%m-%d"),
            seen_ads=False,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
        )
    
    async def find_join_req(self, id):
        return bool(await self.request.find_one({'id': id}))
        
    async def add_join_req(self, id):
        await self.request.insert_one({'id': id})

    async def del_join_req(self):
        await self.request.drop()
        
    async def set_stream_link(self,link):
        await self.stream_link.update_one({} , {'$set': {'link': link}} , upsert=True)
    async def get_stream_link(self):
        link = await self.stream_link.find_one({})
        if link is not None:
            return link.get("link")
        else:
            return None
    async def del_stream_link(self):
        try: 
            isDeleted = await self.stream_link.delete_one({})
            if isDeleted.deleted_count > 0:
                return True
            else:
                return False
        except Exception as e:
            print(f"Got err in db set : {e}")
            return False
        
        
    #get user from database
    async def get_user(self, id):
        user = await self.col.find_one({'id': int(id)})
        return False if not user else user
    
    # reset fiiles count of user
    async def reset_daily_files_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return
        await self.col.update_one({"id": user_id}, {"$set": {"files_count": 0, "last_reset": datetime.now().strftime("%Y-%m-%d")}})

    # reset files count for all user forcefully
    async def reset_all_files_count(self):
        await self.col.update_many({}, {"$set": {"files_count": 0, "last_reset": datetime.now().strftime("%Y-%m-%d")}})

    # reset verification status of user
    async def reset_verification_status(self):
        await self.col.update_many({}, {"$set": {"verified": False}})

    async def is_user_joined(self, id):
        user = await self.col.find_one({"id": id})
        if user is None:
            return False
        return user.get("user_joined")

    async def reset_all_users_joined(self):
        await self.col.update_many({}, {"$set": {"user_joined": False}})

    async def is_premium_status(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return False  # User not found in the database
        return user.get("Premium", False)
    
    async def get_all_premium_users(self):
        return self.col.find({"Premium": True})
    
    async def total_premium_users_count(self):
        count = await self.col.count_documents({"Premium": True})
        return count

    # add user as premium
    async def add_user_as_premium(self, user_id, expiry_date, subscription_date):
        await self.col.update_one(
            {"id": user_id},
            {"$set": {"Premium": True, "premium_expiry": expiry_date, "purchase_date": subscription_date}}
        )

    # remove user from premium
    async def remove_user_premium(self, user_id):
        await self.col.update_one({"id": user_id}, {"$set": {"Premium": False, "premium_expiry": None, "purchase_date": None}})
        
    # remove all premium users forcefully
    async def remove_all_premium_users(self):
        await self.col.update_many({}, {"$set": {"Premium": False, "premium_expiry": None, "purchase_date": None}})

    # remove_all_free_users
    async def remove_all_free_users(self):
        await self.col.delete_many({"Premium": False})
         
    # check user is expired or not if expired then remove premium
    async def check_expired_users(self, user_id):
        user = await self.col.find_one({"id": user_id})

        if user is None:
            return

        duration = user.get("premium_expiry")

        if duration is None:
            return

        purchase = user.get("purchase_date")
        purchased_date = datetime.fromtimestamp(purchase)
        expiry_date = purchased_date + timedelta(days=duration)
        days_left = (expiry_date - datetime.now()).days

        if days_left < 0:
            await self.remove_user_premium(user_id)
            return "Your subscription has expired."
         
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)
   
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        b_users = [user['id'] async for user in users]
        return b_users
    
    async def fetch_value(self, user_id, key):
        user = await self.col.find_one({"id": user_id})
        return user.get(key)

    async def update_value(self, user_id, key, value):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            await self.add_user(user_id, "Anonymous")
            return
        await self.col.update_one({"id": user_id}, {"$set": {key: value}})

    async def get_refferal_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        return user.get("referral")

    async def update_refferal_count(self, user_id, count):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            await self.add_user(user_id, "Anonymous")
        await self.col.update_one({"id": user_id}, {"$set": {"referral": count}})     

    async def get_lifetime_files_count(self, user_id):
        user = await self.col.find_one({"id": user_id})
        if user is None:
            return 0
        return user.get("lifetime_files")       


db = Database(DATABASE_URI, DATABASE_NAME)
