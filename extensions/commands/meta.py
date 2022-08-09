import discord

from discord.ext import commands
from discord import app_commands
from utils.utils import Embed
from components.meta import CodeRunModal

import time
from datetime import datetime
from humanfriendly import format_timespan


class Meta(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    meta = app_commands.Group(name="meta", description="Get infomation about the bot")

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
            description=f"**Druk Online For**: `{format_timespan(uptime)}`\n**Since**: `{time_started.strftime('%d/%m/%Y %H:%M:%S')}`",
        )

        await ctx.response.send_message(embed=embed)

    @meta.command(name="ping", description="Tells you the latency of the bot")
    async def ping(self, ctx: discord.Interaction):
        l = self.bot.latency
        l = round(l, 3)
        p = time.perf_counter()
        await ctx.response.send_message("Pong!")
        embed = Embed(title="Ping", timestamp=discord.utils.utcnow())
        embed.add_field(name="Websocket Latency", value=l * 1000, inline=False)
        embed.add_field(
            name="Bot Latency",
            value=round(time.perf_counter() - p, 3) * 1000,
            inline=False,
        )
        await ctx.edit_original_response(embed=embed)

    @meta.command(name="run", description="Run python code!!")
    async def run(self, ctx: discord.Interaction):
        if not (ctx.user.id in self.bot.owner_ids):
            return await ctx.response.send_message(
                "You are not allowed to use this command!"
            )
        await ctx.response.send_modal(CodeRunModal(self.bot))

    @meta.command(name="kill", description="Stops the bot")
    async def kill(self, ctx: discord.Interaction):
        if ctx.user.id not in self.bot.owner_ids:
            raise
        await ctx.response.send_message("Stopping Druk!")
        exit()


async def setup(bot):
    await bot.add_cog(Meta(bot))
