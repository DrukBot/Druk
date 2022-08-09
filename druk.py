import os
import dotenv
import discord
import utils.utils as utils
from datetime import datetime


from discord.ext import commands


dotenv.load_dotenv()


EXTENSIONS = (
    "extensions.commands.confessions",
    "extensions.commands.misc",
    "extensions.commands.report",
    "extensions.commands.meta",
    "extensions.commands.moderation",
    "extensions.events.error_handler",
)


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
            owner_ids=(
                391973133965328385,
                859996173943177226,
                268815279570681857,
            ),
            allowed_mentions=allowed_mentions,
        )

        self.token: str = os.environ["TOKEN"]
        self.starting_time = datetime.now().timestamp()
        self.invite_link = discord.utils.oauth_url(
            client_id=os.environ["APP_ID"],
            permissions=discord.Permissions(permissions=8),
            scopes=["bot", "applications.commands"],
        )
        self.extensions_list = EXTENSIONS

    async def setup_hook(self) -> None:
        utils.log("Loading All Extensions...")
        for ext in EXTENSIONS:
            try:
                await self.load_extension(ext)
                log_ext = ext.split(".")[-1]
                log_ext = log_ext.replace("_", " ").title()
                utils.log(f"Loaded Extension: {log_ext}")
            except Exception as e:
                print(e)
        utils.log("All Extensions Loaded Successfully.")

        await self.tree.sync()

    async def on_ready(self) -> None:
        utils.log(f"Logged in as {self.user}")
