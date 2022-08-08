import discord


from discord import app_commands
from discord.ext import commands

from utils.utils import Embed


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.CommandTree.error()
    async def app_command_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        error = getattr(error, "original", error)

        if isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Missing Permissions",
                    f"You are missing **{', '.join(error.missing_permissions)}** permission(s) to run this command.",
                )
            )

        else:
            raise error


async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
