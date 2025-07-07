import os
from typing import List

IS_FSUB = bool(os.environ.get("FSUB", True)) # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002008497819 -1002108042638").split()))

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "7699848766:AAGHoAYw7uAd01N-1beOeaZdPgJ51K1anIE")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "21184495"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "7238819d51a5280143fc3023a2f1abed")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "8110231942"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://akashrabha2005:781120@cluster0.pv6yd2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "savecontentbot")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1002748718005"))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
