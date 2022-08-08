import discord
from discord.ext import commands
import utils
import traceback
import textwrap


class CodeRunModal(discord.ui.Modal):
    code = discord.ui.TextInput(
        label="Python Code",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=2,
        max_length=4000,
    )

    def __init__(self, bot: commands.Bot):
        super().__init__(title="Execute Python Code!")

    async def on_submit(self, ctx: discord.Interaction) -> None:
        data = self.code.value
        bot = self.bot
        try:
            args = {
                **globals(),
                "author": ctx.user,
                "channel": ctx.channel,
                "guild": ctx.guild,
                "client": self.bot,
                "bot": self.bot,
                "imp": __import__,
            }
            data = data.replace("”", '"').replace("“", '"')
            while data.startswith((' ','\t','\n')):
                data = data[1:]
            split = data.splitlines()
            if len(split) == 1:
                if not data.startswith("yield"):
                    data = f"yield {data}"
            data = textwrap.indent(data, "    ")
            exec(f"async def func():\n{data}", args)
            async for resp in eval("func()", args):
                resp = str(resp).replace(bot.token, "[TOKEN]")
                await ctx.channel.send(resp)
        except:
            error = traceback.format_exc()
            await ctx.channel.send(
                embed=utils.Embed.ERROR(
                    title="Uh Oh!",
                    description=f"```py\n{error}```",
                )
            )


