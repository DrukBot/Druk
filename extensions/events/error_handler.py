import traceback
import discord


from discord import app_commands
from discord.ext import commands
import utils


class ErrorHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        bot.tree.error(self.app_command_error)

    async def app_command_error(
        self, ctx: discord.Interaction, error: app_commands.AppCommandError
    ):
        error = getattr(error, "original", error)

        if isinstance(error, app_commands.errors.MissingPermissions):
            await ctx.response.send_message(
                embed=utils.Embed.ERROR(
                    "Missing Permissions",
                    f"You are missing **{', '.join(error.missing_permissions)}** permission(s) to run this command.",
                )
            )

        if isinstance(error, app_commands.CommandOnCooldown):
            await ctx.response.send_message(
                embed=utils.Embed.ERROR(
                    "On Cooldown",
                    f"You can use command **`{ctx.command.name}`** again after **{error.retry_after:.2f}** seconds!",
                )
            )

        else:
            try:
                await ctx.response.send_message(
                    embed=utils.Embed.ERROR(
                        "Uh oh!",
                        f"```\n{traceback.format_exc()}\n```",
                    )
                )
                utils.log(error, "error")
            except discord.errors.InteractionResponded:
                await ctx.edit_original_response(
                    embed=utils.Embed.ERROR(
                        "Uh oh!",
                        f"```\n{traceback.format_exc()}\n```",
                    )
                )
                utils.log(error, "error")



async def setup(bot):
    await bot.add_cog(ErrorHandler(bot))
