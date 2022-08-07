import discord

from discord.ext import commands
from discord import app_commands
from utils.utils import Embed

from datetime import datetime
from humanfriendly import format_timespan


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    meta = app_commands.Group(name="meta", description="Get infomation about the bot")

    @meta.command(name="latency", description="Returns the latency of the bot")
    async def latency(self, ctx: discord.Interaction):

        latency = self.bot.latency
        latency = round(latency, 3)

        embed = Embed(title="Latency", timestamp=discord.utils.utcnow())

        embed.add_field(name="Seconds", value=latency)

        await ctx.response.send_message(embed=embed)

    @meta.command(
        name="servers", description="The total number of servers the bot is in"
    )
    async def servers(self, ctx: discord.Interaction):

        total_members = 0
        total_bots = 0

        for g in self.bot.guilds:
            for m in g.members:
                if m.bot:
                    total_bots += 1
                else:
                    total_members += 1

        embed = Embed(
            title="Servers",
            description=f"**Total Servers** `{len(self.bot.guilds)}`\n**Total Members** `{total_members}`\n**Total Bots** `{total_bots}`",
            timestamp=discord.utils.utcnow(),
        )

        await ctx.response.send_message(embed=embed)

    @meta.command(name="uptime", description="Tells you the uptime of the bot")
    async def uptime(self, ctx: discord.Interaction):

        time_started = datetime.fromtimestamp(self.bot.starting_time)

        uptime = datetime.now().timestamp() - self.bot.starting_time

        embed = Embed(
            title="Uptime",
            description=f"{format_timespan(uptime)}\n**Started**: `{time_started.strftime('%d/%m/%Y %H:%M:%S')}`",
        )

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Meta(bot))
