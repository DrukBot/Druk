import discord
from os import system, getcwd

from discord.ext import commands
from discord import app_commands
from utils.utils import Embed
from components.meta import CodeRunModal

from time import time
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

        start = time()
        await ctx.response.send(content="Pinging...")
        end = time()
        embed = Embed(f"Latency: `{self.bot.latency*1000:,.0f} ms`\nResponse Time: `{(end-start)*1000:,.0f} ms`")
        await ctx.edit_original_message(content="Pong!", embed=embed)


    @meta.command(name="run", description="Run python code!!")
    async def run(self, ctx: discord.Interaction):
        if not (ctx.user.id in self.bot.owner_ids):
            return await ctx.response.send_message(
                "You are not allowed to use this command!", ephemeral=True
            )
        await ctx.response.send_modal(CodeRunModal(self.bot))

    @meta.command(name="kill", description="Stops the bot")
    async def kill(self, ctx: discord.Interaction):
        if ctx.user.id not in self.bot.owner_ids:
            await ctx.response.send_message(
                embed=Embed.ERROR("Permissions!", "You cannot do that!"), ephemeral=True
            )
            return
        await ctx.response.send_message("Stopping Druk!")
        await self.bot.close()
        system("pm2 stop Druk")

    @meta.command(name="restart", description="Restarts the bot")
    async def restart(self, ctx: discord.Interaction):
        if ctx.user.id not in self.bot.owner_ids:
            await ctx.response.send_message(
                embed=Embed.ERROR("Permissions!", "You cannot do that!"), ephemeral=True
            )
            return
        await ctx.response.send_message("Restarting bot!")
        await self.bot.close()
        system("pm2 restart Druk")

    @meta.command(
        name="update", description="Updates the bot to the newest github commit"
    )
    async def update(self, ctx: discord.Interaction):
        if ctx.user.id not in self.bot.owner_ids:
            await ctx.response.send_message(
                embed=Embed.ERROR("Permissions!", "You cannot do that!"), ephemeral=True
            )
            return
        if getcwd() == "/root/Druk":
            system("git pull")
            await ctx.response.send_message("Updating bot!")
            await self.bot.close()
            system("pm2 restart Druk")
        else:
            system("cd /root/Druk")
            system("git pull")
            await ctx.response.send_message("Updating bot!")
            await self.bot.close()
            system("pm2 restart Druk")


async def setup(bot):
    await bot.add_cog(Meta(bot))
