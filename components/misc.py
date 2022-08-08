import discord
from discord.ext import commands
import jishaku
import utils


class JSKPyModal(discord.ui.Modal):
    code = discord.ui.TextInput(
        label="Code",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=2,
        max_length=10000,
    )

    def __init__(self, bot: commands.Bot):
        super().__init__(title="Jishaku Execute")

    async def on_submit(self, ctx: discord.Interaction) -> None:
        await ctx.defer()
        await ctx.response.send_message()


