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

    async def registerUser(self, ctx: discord.Interaction, user: discord.User):
        if user.bot:
            return await ctx.response.send_message("Bot's can't be registered!")
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")
        if acc:
            await ctx.response.send_message("You are already a registered user!", ephemeral=True)
            return

        embed = Embed(title="Breaking these rules can be resulting in ban/deletion/reset of you account.", description="RULES TO BE FOLLOWED").set_author(name="Druk Rules!", icon_url=self.bot.user.display_avatar.url)
        await ctx.response.send_message(content=user.mention, embed=embed, view=RegisterUser(user, self.db))


    async def getUserAccount(self, ctx: discord.Interaction, user: typing.Union[discord.User, discord.Member]):
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")

        if acc is None:
            embed = Embed(description=f"{user} is not registered user.\n\nUse `/register` command to create you account.").set_author(name="User Not Registered!", icon_url=user.display_avatar.url)
            await ctx.response.send_message(embed=embed)
            return 


        return acc


    async def getUserSettings(self, ctx, user: typing.Union[discord.User, discord.Member]):
        acc_settings = await self.db.fetch('settings', f"user_id = {user.id}")

        if acc_settings is None:
            embed = Embed(description=f"{user} is not registered user.\n\nUse `/register` command to create you account.").set_author(name="User Not Registered!", icon_url=user.display_avatar.url)
            await ctx.response.send_message(embed=embed)
            return

        return acc_settings


    @app_commands.command(name="register")
    async def register(self, ctx: discord.Interaction):
        await self.registerUser(ctx, ctx.user)
        

    @app_commands.command(name='work')
    @app_commands.checks.cooldown(1, 120)
    async def work(
        self,
        ctx: discord.Interaction,
    ):
        acc = await self.getUserAccount(ctx, ctx.user)
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
        acc = await self.getUserAccount(ctx, user)
        userSettings = await self.getUserSettings(ctx, user)

        if userSettings["privacy"] and user != ctx.user:
            await ctx.response.send_message(f"**{user}** has his wallet private.", ephemeral=True)
            return

        if user.bot:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(user.id)), ephemeral=True)
            return    

        coins, cash = acc['coins'], acc['cash']

        walletEmbed = discord.Embed(description="**Wallet**").set_author(name=user, icon_url=user.display_avatar.url)
        walletEmbed.add_field(name="Coins", value=coins)
        walletEmbed.add_field(name="Cash", value=cash)

        if user.id != ctx.user.id:
            walletEmbed.set_footer(text=f"Requested by {ctx.user}")

        await ctx.response.send_message(embed=walletEmbed)


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
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah there", "You can't be trying to steal money, only use positive numbers"))
            return

        senderAccount = await self.getUserAccount(ctx, ctx.user)
        recipientAccount = await self.getUserAccount(ctx, recipient)

        if senderAccount['coins'] < amount:
            insufficient_embed = discord.Embed(title="Insufficient Funds!", description=f"You only have {senderAccount['coins']} coins.\nYou are {amount - senderAccount['coins']} coins short!")
            await ctx.response.send_message(embed=insufficient_embed)
            return
        await self.db.update('accounts', {'coins': senderAccount['coins']-amount}, f'user_id = {ctx.user.id}')
        await self.db.update('accounts', {'coins': recipientAccount['coins']+amount}, f'user_id = {recipient.id}')

        successEmbed = Embed(description=f"Transfered `{amount}` Credits to **{recipient}** Account.").set_author(name=ctx.user, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=successEmbed)



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
