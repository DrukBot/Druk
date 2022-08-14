from distutils.command.build_ext import extension_name_re
import discord
from discord.ext import commands
from discord import app_commands
from utils.utils import Embed
import errors.dataExceptions


class Help(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    help = app_commands.Group(name="help", description="Get help with the bot")

    @help.command(name="all", description="Shows help about all commands")
    async def all(self, ctx: discord.Interaction):

        extensions = self.bot.extensions_list
        
        embed_list = []

        for ext in extensions:
            ext_name = ext.split(".")[-1]
            cog = self.bot.get_cog(ext)
            if cog is None:
                raise errors.dataExceptions.GotNone()
            embed_list.append(Embed(title=ext_name, description=[c.qualified_name for c in cog.walk_commands()]))

        await ctx.response.send_message(embeds=embed_list)        


async def setup(bot):
    await bot.add_cog(Help(bot))
