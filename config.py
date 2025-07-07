import os

# Bot token @Botfather
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8180204910:AAFvuh6PYkOKXvZ4tZIRzZLWjaOacKZeowc")

# Your API ID from my.telegram.org
API_ID = int(os.environ.get("API_ID", "27705761"))

# Your API Hash from my.telegram.org
API_HASH = os.environ.get("API_HASH", "822cb334ca4527a134aae97f9fe44fd6")

# Your Owner / Admin Id For Broadcast 
ADMINS = int(os.environ.get("ADMINS", "6165669080"))

# Your Mongodb Database Url
# Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_URI = os.environ.get("DB_URI", "mongodb+srv://akashrabha2005:781120@cluster0.pv6yd2f.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0") # Warning - Give Db uri in deploy server environment variable, don't give in repo.
DB_NAME = os.environ.get("DB_NAME", "vjsavecontentbot")
DB_CHANNEL = int(os.environ.get("DB_CHANNEL", "-1001234567890"))

# If You Want Error Message In Your Personal Message Then Turn It True Else If You Don't Want Then Flase
ERROR_MESSAGE = bool(os.environ.get('ERROR_MESSAGE', True))
