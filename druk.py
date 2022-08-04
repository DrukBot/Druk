import os
import dotenv
import asyncio
import discord
import aiosqlite
import utils.utils as utils


from discord.ext import commands
from datetime import datetime
from colorama import Fore, Style

dotenv.load_dotenv()

EXTENSIONS = ("extensions.commands.confessions",)


class Druk(commands.Bot):
    def __init__(self):
        allowed_mentions = discord.AllowedMentions(
            everyone=False, roles=False, users=True
        )
        intents = discord.Intents.default()
        intents.members = True
        super().__init__(
            command_prefix="d.",
            intents=intents,
            application_id=int(os.environ["APP_ID"]),
            allowed_mentions=allowed_mentions,
        )

        self.token: str = os.environ["TOKEN"]

    async def setup_hook(self) -> None:
        utils.log("Loading All Extensions...")
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
            except Exception as e:
                print(e)
        utils.log("All Extensions Loaded Successfully.")

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
