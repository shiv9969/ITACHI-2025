import re
from os import environ

id_pattern = re.compile(r'^.\d+$')
def is_enabled(value, default):
    if value.lower() in ["true", "yes", "1", "enable", "y"]:
        return True
    elif value.lower() in ["false", "no", "0", "disable", "n"]:
        return False
    else:
        return default

# Bot information
API_ID = environ.get('API_ID', "18029060")
API_HASH = environ.get('API_HASH', "c7e952440251e33bb5cce566b29f7254")
BOT_TOKEN = environ.get('BOT_TOKEN', "7577211428:AAFLJsGuTKDhc8wZ_V11AncTYcjmzRSYNyA")
# Admins, Channels & Users
ADMINS = [int(admin) if id_pattern.search(admin) else admin for admin in environ.get('ADMINS', '1991522624 1844994992 1525203313').split()]
CHANNELS = [int(ch) if id_pattern.search(ch) else ch for ch in environ.get('CHANNELS', '-1001971879597 -1001882174994').split()]

auth_grp = environ.get('AUTH_GROUP', "0") # DONE 
AUTH_GROUPS = [int(ch) for ch in auth_grp.split()] if auth_grp else None
INDEX_USER = [int(environ.get('INDEX_USER', '1525203313'))]
INDEX_USER.extend(ADMINS)

# MongoDB information
DATABASE_URI = environ.get('DATABASE_URI', "mongodb+srv://bob2025:bob2025@cluster0.vuo6h.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
DATABASE_NAME = environ.get('DATABASE_NAME', "ITACHI_V2")
COLLECTION_NAME = environ.get('COLLECTION_NAME', 'ITACHI_2025')

# Force Subscribe
auth_channel = environ.get('AUTH_CHANNEL', '-1002077157127')
AUTH_CHANNEL = int(auth_channel) if auth_channel and id_pattern.search(auth_channel) else None

# Others
LOG_CHANNEL = int(environ.get('LOG_CHANNEL', "-1001844691460"))
FORCESUB_CHANNEL = int(environ.get('FORCESUB_CHANNEL', "0"))
SLOW_MODE_DELAY = int(environ.get('SLOW_MODE_DELAY', 10))
WAIT_TIME = int(environ.get('AUTO_DELETE_WAIT_TIME', 600))
FORWARD_CHANNEL = int(environ.get('FORWARD_CHANNEL', "0"))
FREE_LIMIT = int(environ.get('FREE_LIMIT', 1))

# extra
REDEEM_ACCESS_KEY = environ.get("LICENSE_ACCESS_KEY", "H06M6LEXC5C02UPI2KFD")
REDEEM_BASE_URL = environ.get("LICENSE_BASE_URL", "https://redeem.razi.dev")
REQUEST_GROUP = environ.get("REQUEST_GROUP_LINK", "https://t.me/bob_files1")
AD_IMG = environ.get("AD_IMG", "https://graph.org/file/b2f7f0ab92021e07c13c2.jpg")

# STREEMING
STREAM_BTN = is_enabled((environ.get('STREAM_BTN', "True")), False) #Streeming Off Karna Ho Tab False kar Do
STREAM_SITE = (environ.get('STREAM_SITE', 'shortxlinks.com')) #Shortner Website
STREAM_API = (environ.get('STREAM_API', 'dd5303bb44fa8da37e0ea9164c138b5c3d685583'))
STREAM_MODE = is_enabled((environ.get('STREAM_MODE', "False")), False) # Agar Streem Me Shortner Lagana Ho to True Kar Dena

BIN_CHANNEL = int(environ.get('BIN_CHANNEL', -1002178176007)) #same As File Streem Bot
URL = environ.get("URL", "https://f2lx-70359b01db6d.herokuapp.com/")
