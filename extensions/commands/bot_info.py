from platform import python_version
import discord

from discord.ext import commands
from discord import app_commands
from components import paginator

import utils
from pathlib import Path
import cpuinfo
from psutil import virtual_memory, cpu_percent
from datetime import datetime

class botInfo(commands.Cog, name="Bot Info"):
    def __init__(self, bot):
        self.bot = bot


    def convert_size(self, bytes, suffix="B"):
        factor = 1024
        for unit in ["", "K", "M", "G", "T", "P"]:
            if bytes < factor:
                return f"{bytes:.2f}{unit}{suffix}"
            
            bytes /= factor

    
    @app_commands.command(name="uptime")
    async def uptime(
        self,
        ctx: discord.Interaction
    ):
        uptime = datetime.now().timestamp() - self.bot.starting_time

        uptime_embed = discord.Embed(title="Uptime", cor=discord.Color.red())
        uptime_embed.add_field(name="Up for", value=f"{uptime} seconds")

        await ctx.response.send_message(embed=uptime_embed)

    @app_commands.command(name="hardware-info")
    async def hardwareinfo(
        self,
        ctx: discord.Interaction
    ):
        hw_embed = discord.Embed(title="Hardware Info", color=discord.Color.red())

        cpu = cpuinfo.get_cpu_info()['brand_raw']
        cpu_usage = cpu_percent()
        ram = self.convert_size(virtual_memory().total)
        space = self.convert_size(sum(f.stat().st_size for f in Path(self.bot.root_directory).glob('**/*') if f.is_file()))
        pver = python_version()

        hw_embed.add_field(name="CPU", value=cpu, inline=False)
        hw_embed.add_field(name="CPU Usage", value=f"{cpu_usage}%", inline=False)
        hw_embed.add_field(name="RAM", value=ram, inline=False)
        hw_embed.add_field(name="Storage Space", value=space, inline=False)
        hw_embed.add_field(name="Python Version", value=pver)

        await ctx.response.send_message(embed=hw_embed)

        
    @app_commands.command(name="servers")
    async def servers(
        self,
        ctx: discord.Interaction
    ):

        total_members = 0
        total_bots = 0

        for g in self.bot.guilds:
            for m in g.members:
                if m.bot:
                    total_bots += 1
                else:
                    total_members += 1

        embed = utils.Embed(
            title="Servers",
            description=f"**Total Servers** `{len(self.bot.guilds)}`\n**Total Members** `{total_members}`\n**Total Bots** `{total_bots}`",
            timestamp=discord.utils.utcnow(),
        )

        await ctx.response.send_message(embed=embed)

    
    @app_commands.command(name="detailed-servers")
    async def detailedservers(
        self,
        ctx: discord.Interaction
    ):
        if ctx.user.id not in self.bot.owner_ids:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Whoops", "You don't have permission to do that"))
            return
        
        await ctx.response.defer()

        pag = commands.Paginator('', '', max_size=160)
        
        g: discord.Guild

        for g in self.bot.guilds:
            members = 0
            bots = 0
            invite = None
            for u in g.members:
                if u.bot:
                    bots += 1
                else:
                    members += 1

            for c in g.channels:
                try:
                    invite = await c.create_invite()
                    break
                except:
                    pass

            pag.add_line(f"Name: {g.name}\nOwner: {g.owner}\nOwner ID: {g.owner.id}\nMembers: {members}\nBots: {bots}\nInvite: {invite.url}")
        server_embed = discord.Embed(title="Servers", color=discord.Colour.green(), description=pag.pages[0])
        view = paginator.PaginatorView(pag, ctx.user, embed= server_embed)

        await ctx.edit_original_response(view=view, embed=server_embed)


async def setup(bot):
    await bot.add_cog(botInfo(bot))
    