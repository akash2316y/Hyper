from pyrogram import Client
from config import API_ID, API_HASH

class Bot(Client):
    def __init__(self):
        super().__init__(
            "techvj login",    # Session name ➔ will generate .session file
            api_id=API_ID,
            api_hash=API_HASH,
            plugins=dict(root="plugins"),
            workers=50,
            sleep_threshold=10
        )

    async def start(self):
        await super().start()
        print('Userbot Started')

    async def stop(self, *args):
        await super().stop()
        print('Userbot Stopped')

Bot().run()
