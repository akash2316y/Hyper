import os
from typing import List

IS_FSUB = bool(os.environ.get("FSUB", True)) # Set "True" For Enable Force Subscribe
AUTH_CHANNELS = list(map(int, os.environ.get("AUTH_CHANNEL", "-1002008497819 -1002108042638").split()))

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8105389323:AAEDkzjyNZXrcaYbq1BK_QYX87nH5_cO_S4")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "20715688"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "6fd4f5071acac391de47d8af73803b80")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "8110231942"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://akashrabha2005:781120@cluster0.pv6yd2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "savecontentbot")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1002748718005"))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
