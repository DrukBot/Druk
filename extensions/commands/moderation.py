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
            Choice(name="seconds"),
            Choice(name="minutes"),
            Choice(name="hours")
        ]
    )
    @app_commands.checks.has_permission(manage_channels=True, administrator=True)
    async def slowmode(self, ctx: discord.Interaction, time: int, measure: Choice[str]):
        if time == 0:
            await ctx.channel.slowmode_delay(time)
            embed = Embed.SUCCESS(
                "Slowmode Disabled", "Slowmode has now been disabled in this channel"
            )
        else:  
            if measure.name == "seconds":
                pass
            elif measure.name == "minutes":
                slowmode_seconds = time * 60
            elif measure.name == "hours":
                slowmode_seconds = time * 3600

            await ctx.channel.slowmode_delay(slowmode_seconds)

            embed = Embed.SUCCESS(
                "Slowmode Enabled", f"Slowmode has been set to {time}{measure.name}"
            )

        await ctx.response.send_message(embed=embed)

