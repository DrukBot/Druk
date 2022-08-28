import os
import paramiko
import typing
import discord
import utils.utils as utils
from datetime import datetime


from discord.ext import commands
from components.report import ReportAction



EXTENSIONS: typing.Final[typing.Tuple[str, ...]] = (
    "extensions.commands.confessions",
    "extensions.commands.misc",
    "extensions.commands.report",
    "extensions.commands.meta",
    "extensions.commands.moderation",
    "extensions.commands.economy",
    "extensions.commands.bot_info",
    "extensions.events.error_handler"
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
        discord.utils.setup_logging()
        self.token: str = os.environ["TOKEN"]
        self.root_directory = "."
        self.starting_time = datetime.now().timestamp()
        self.ssh_session = paramiko.SSHClient()
        self.ssh_session.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.ssh_session.connect(os.environ['SSHIP'], 22, os.environ['SSHUSER'], os.environ['SSHPASS'], allow_agent=False, look_for_keys=False, timeout = 10)
        utils.log(f"Successfully started ssh session as {os.environ['SSHIP']}")
        self.invite_link = discord.utils.oauth_url(
            client_id=os.environ["APP_ID"],
            permissions=discord.Permissions(permissions=8),
            scopes=["bot", "applications.commands"],
        )
        self.extensions_list = EXTENSIONS
        self.cog_list = (
            "Bot Info",
            "Economy",
            "Report",
            "Confessions",
            "Miscellaneous"
        )
        self.add_persistent_views = False

    async def setup_hook(self) -> None:
        if not self.add_persistent_views:
            self.add_view(ReportAction())
            self.add_persistent_views = True
            utils.log("Persistent views added")

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

    async def log_webhook(self, embed: discord.Embed, *, content: typing.Optional[str]=None):
        session = self.http._HTTPClient__session
        webhook = discord.Webhook.partial(id=int(os.environ["LOG_WEBHOOK_ID"]), token=os.environ["LOG_WEBHOOK_TOKEN"], session=session)
        await webhook.send(content=content, embed=embed)
