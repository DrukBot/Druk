from pydoc import describe
from tkinter import S
import discord
import random
import utils
import typing

from discord.ext import commands
from discord import app_commands

from components import (
    paginator,
)

from utils.utils import Embed
from components.economy import RegisterUser

class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db: utils.Database = utils.Database("economy", [accounts_table, settings_table])

    async def cog_load(self) -> None:
        await self.db.connect()

    async def register(self, ctx: discord.Interaction, user: discord.User):
        if user.bot:
            await ctx.followup.send("Bot's can't be registered!")
        acc = self.db.fetch('accounts', f"user_id = {user.id}")
        if acc:
            await ctx.response.send_message("You are already a registered user!", ephemeral=True)
            return

        embed = Embed(title="Breaking these rules can be resulting in ban/deletion/reset of you account.", description="RULES TO BE FOLLOWED").set_author(name="Druk Rules!", icon_url=self.bot.display_avatar.url)
        await ctx.followup.send(embed=embed, view=RegisterUser(user, self.db))


    async def get_user_account(self, ctx: discord.Interaction, user: typing.Union[discord.User, discord.Member]):
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")

        if acc:
            return acc
        embed = Embed(description=f"{user} is not registered user.\n\nUse `/register` command to create you account.").set_author(name="User Not Registered!", icon_url=user.display_avatar.url)
        await ctx.response.send_message(embed=embed)
    

    async def get_user_settings(self, ctx, user: typing.Union[discord.User, discord.Member]):
        S = await self.db.fetch('settings', f"user_id = {user.id}")

        if s:
            return s
        embed = Embed(description=f"{user} is not a registered user.\n\nUse `/register` command to create you account.").set_author(name="User Not Registered!", icon_url=user.display_avatar.url)
        await ctx.response.send_message(embed=embed)


    @app_commands.command(name="register")
    async def _register(self, ctx: discord.Interaction):
        await self.register(ctx, ctx.user)
        

    @app_commands.command(name='work')
    @app_commands.checks.cooldown(1, 120)
    async def work(
        self,
        ctx: discord.Interaction,
    ):
        acc = await self.check_and_fetch_account(ctx, ctx.user)
        cs = random.randint(50, 400)
        await self.db.update('accounts', {'coins': acc['coins']+cs}, f"user_id = {ctx.user.id}")
        await ctx.response.send_message(
            embed=discord.Embed(
                title="You have finished working!",
                description=f"You have earned **`{cs}`** coins!",
            )
        )

    @app_commands.command(name='wallet')
    async def wallet(
        self,
        ctx: discord.Interaction,
        user: typing.Optional[discord.User] = None,
    ):  
        user = user or ctx.user
        acc = await self.get_user_account(ctx, user)
        settings = self.get_user_settings(ctx, user)

        if settings["privacy"] is True and user != ctx.user:
            return await ctx.response.send_message(f"**{user}** has his wallet private.", ephemeral=True)

        if user.bot:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(user.id)), ephemeral=True)   

        coins, cash = acc['coins'], acc['cash']

        wE = discord.Embed(description="**Wallet**").set_author(name=user, icon_url=user.display_avatar.url)
        wE.add_field(name="Coins", value=coins)
        wE.add_field(name="Cash", value=cash)

        if user.id != ctx.user.id:
            wE.set_footer(text=f"Requested by {ctx.user}")

        await ctx.response.send_message(embed=wE)


    @app_commands.command(name='leaderboard')
    async def leaderboard(
        self, ctx: discord.Interaction,
    ):
        accs = await self.db.fetch('accounts', all=True, order_by='coins DESC')
        pag = paginator.Paginator(page_size = 100 )
        for i, acc in enumerate(accs):
            mem = ctx.guild.get_member(acc['user_id'])
            if mem is None:
                await self.db.delete('accounts', f"user_id = {acc['user_id']}")
            pag.add_line(f"{i+1}. {mem} - {acc['coins']} coins")
        em = discord.Embed(colour = discord.Color.red(), title="Leaderboard", description=pag.pages[0])
        em.set_footer(text=f"Requested by {ctx.user}", icon_url=ctx.user.display_avatar.url)
        v = paginator.PaginatorView(pag, ctx.user, embed = em)
        await ctx.response.send_message(view = v, embed = em)


    @app_commands.command(name="transfer")
    async def transfer(
        self,
        ctx: discord.Interaction,
        recipient: discord.User,
        amount: int
    ):
        if amount < 1:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah there!", "You can't be trying to steal money, only use positive numbers"))
            return

        sa = await self.get_user_ccount(ctx, ctx.user)
        ra = await self.get_user_account(ctx, recipient)

        if sa['coins'] < amount:
            insufficient_embed = discord.Embed(title="Insufficient Funds!", description=f"You only have {sa['coins']} coins.\nYou are {amount - sa['coins']} coins short!")
            await ctx.response.send_message(embed=insufficient_embed)
            return
        await self.db.update('accounts', {'coins': sa['coins']-amount}, f'user_id = {ctx.user.id}')
        await self.db.update('accounts', {'coins': ra['coins']+amount}, f'user_id = {recipient.id}')

        se = Embed(description=f"Transfered `{amount}` Credits to **{recipient}** Account.").set_author(name=ctx.user, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=se)



accounts_table = utils.Table(
    "accounts",
    [
        utils.Column("user_id", int),
        utils.Column("coins", int),
        utils.Column("cash", int),
    ],
    primary_key="user_id",
)

settings_table = utils.Table(
    "settings",
    [
        utils.Column("user_id", int),
        utils.Column("pings", bool),
        utils.Column("privacy", bool)
    ],
    primary_key="user_id"
)

async def setup(bot):
    await bot.add_cog(Economy(bot))
