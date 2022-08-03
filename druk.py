import os
import dotenv
import asyncio
import discord
import aiosqlite
import utils


from discord.ext import commands
from datetime import datetime
from colorama import Fore, Style

dotenv.load_dotenv()

EXTENSIONS = [

]


class Druk(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(everyone=False, roles=False, users=True)
        super().__init__(
            command_prefix="d.",
            intents=discord.Intents.all(),
            application_id=int(os.environ["APP_ID"]),
            allowed_mentions=allowed_mentions
        )

        self.token = os.environ["TOKEN"]


    async def setup_hook(self):
        print(utils.colour("[+] {datetime.utcnow()} | Loading All Extensions...", 'green'))
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(e)
        print(utils.colour("[+] {datetime.utcnow()} | All Extensions Loaded Successfully.", 'green'))

    async def on_ready(self):
        print(utils.colour(f"[+] {datetime.utcnow()} | Logged in as {self.user}", 'green'))

