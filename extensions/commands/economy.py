import discord
import random
import utils
import typing

from discord.ext import commands
from discord import app_commands

import components

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: utils.Database = utils.Database("economy", [accounts_table])

    async def cog_load(self) -> None:
        await self.db.connect()

    async def fetch_or_create_account(self, user: typing.Union[discord.User, discord.Member]) -> typing.Dict[str, typing.Any]:
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")
        if not acc:
            await self.db.insert('accounts', (user.id, 100, 0))
            acc = {'user_id': user.id, 'balance': 100, 'bank': 0}
        return acc

    @app_commands.command(name='work')
    @app_commands.checks.cooldown(1, 120)
    async def work(
        self,
        ctx: discord.Interaction,
    ):
        acc = await self.fetch_or_create_account(ctx.user)
        cs = random.randint(50, 400)
        await self.db.update('accounts', {'coins': acc['coins']+cs}, f"user_id = {ctx.user.id}")
        await ctx.response.send_message(
            embed=discord.Embed(
                title="You have finished working!",
                description=f"You have earned **`{cs}`** coins!",
            )
        )

    @app_commands.command(name='balance')
    async def balance(
        self,
        ctx: discord.Interaction,
        user: typing.Optional[discord.User] = None,
    ):
        user = user or ctx.user
        acc = await self.fetch_or_create_account(ctx.user)
        coins, cash = acc['coins'], acc['cash']
        balEm = discord.Embed(title="Balance", colour = discord.Color.red())
        balEm.add_field(name="Coins", value=coins)
        balEm.add_field(name="Cash", value=cash)
        balEm.set_footer(text=f"Requested by {user}", icon_url=user.display_avatar.url)
        await ctx.response.send_message(embed=balEm)

    @app_commands.command(name='leaderboard')
    async def leaderboard(
        self, ctx: discord.Interaction,
    ):
        accs = await self.db.fetch('accounts', all=True, order_by='coins DESC')
        pag = commands.Paginator('','',linesep='\n\n')
        for i, acc in enumerate(accs):
            pag.add_line(f"{i+1}. {ctx.guild.get_member(acc['user_id'])} - {acc['coins']} coins")
        em = discord.Embed(colour = discord.Color.red(), title="Leaderboard", description=pag.pages[0])
        em.set_footer(text=f"Requested by {ctx.user}", icon_url=ctx.user.display_avatar.url)
        v = components.paginator.Paginator(pag, ctx.user, embed = em)
        await ctx.response.send_message(view = v)


accounts_table = utils.Table(
    "accounts",
    [
        utils.Column("user_id", int),
        utils.Column("coins", int),
        utils.Column("cash", int),
    ],
    primary_key="user_id",
)

async def setup(bot):
    await bot.add_cog(Economy(bot))
