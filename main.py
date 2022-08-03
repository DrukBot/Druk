import os
import dotenv
import asyncio
import discord # pycord or discord.py ?


from discord.ext import commands

dotenv.load_dotenv()

EXTENSIONS = [

]


class Druk(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(everyone=False, role=False)
        super().__init (
            command_prefix="d.",
            intents=discord.Intents.all(),
            application_id=os.environ["APP_ID"],
            allowed_mentions=allowed_mentions
        )

        self.token = os.environ["TOKEN"]
        
    async def setup_hook(self):
        print("Loading All Extensions..")
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(e)
        print("All Extensions Loaded Successfully.")

    async def on_ready(self):
        print("Yoo!")


Druk = Druk()

async def run():
    async with Druk:
        await Druk.start()

if __name__ == "__main__":
    asyncio.run(run())
        