import discord

from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice
from utils.utils import Embed


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    moderation = app_commands.Group(name="moderation", description="Moderation commands for your server")

    @moderation.command(name="slowmode", description="Sets the slowmode duration for the channel")
    @app_commands.choices(
        measure=[
            Choice(name="seconds", value="seconds"),
            Choice(name="minutes", value="minutes"),
            Choice(name="hours", value="hours")
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True, administrator=True)
    async def slowmode(self, ctx: discord.Interaction, time: int, measure: Choice[str]):
        if time == 0:
            await ctx.channel.slowmode_delay(time)
            embed = Embed(
                title="Slowmode Disabled", description="Slowmode has now been disabled in this channel"
            )
        else:  
            if measure.value == "seconds":
                pass
            elif measure.value == "minutes":
                slowmode_seconds = time * 60
            elif measure.value == "hours":
                slowmode_seconds = time * 3600

            await ctx.channel.slowmode_delay(slowmode_seconds)

            embed = Embed(
                title="Slowmode Enabled", description=f"Slowmode has been set to {time}{measure.name}"
            )

        await ctx.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(Moderation(bot))