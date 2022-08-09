import discord
from discord import app_commands
from discord.ext import commands
from components.games import AkinatorView

from utils.utils import Embed

import akinator


class Games(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot
        self.aki = akinator.Akinator()

    games = app_commands.Group(name="games", description="All game commands")

    @games.command(name="akinator-start", description="Starts your akinator game")
    async def akinatorstart(self, ctx: discord.Interaction):
        """
        Removed deferring from the components/games.py view
        The game should loop until it is done but you never know
        """
        question = self.aki.start_game()
        embed = Embed(title="Question 1", description=question)
        await ctx.response.send_message(
            embed=embed, view=AkinatorView(ctx, self.aki, question, q_no=1)
        )


async def setup(bot):
    await bot.add_cog(Games(bot))
