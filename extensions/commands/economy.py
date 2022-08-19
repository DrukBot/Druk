import discord
import random
import utils
import typing

from discord.ext import commands
from discord import app_commands

from components import (
    paginator,
)
from utils.utils import log_webhook

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
            acc = {'user_id': user.id, 'coins': 100, 'cash': 0}
            await log_webhook(embed=discord.Embed(title="Account created", description=f"User: {user.name}"))
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
        if user is None:
            user = ctx.user
        if user.bot:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(user.id)))
            return     
        acc = await self.fetch_or_create_account(user)
        coins, cash = acc['coins'], acc['cash']
        if user is not None:
            balEm = discord.Embed(title=f"**{user.name}** Balance", colour = discord.Color.red())
        else:
            balEm = discord.Embed(title="Balance", colour = discord.Color.red())
        balEm.add_field(name="Coins", value=coins)
        balEm.add_field(name="Cash", value=cash)
        if user.id != ctx.user.id:
            balEm.set_footer(text=f"Requested by {ctx.user}", icon_url=ctx.user.display_avatar.url)
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
        v = paginator.Paginator(pag, ctx.user, embed = em)
        await ctx.response.send_message(view = v, embed = em)


    @app_commands.command(name="transfer")
    async def transfer(
        self,
        ctx: discord.Interaction,
        recipient: discord.User,
        amount: int
    ):  
        if recipient.bot:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(recipient.id)))
            return  
        if amount < 1:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah there", "You can't be trying to steal money, only use positive numbers"))
            return
        sender_acc = await self.fetch_or_create_account(ctx.user)
        recipient_acc = await self.fetch_or_create_account(recipient)
        if sender_acc['coins'] < amount:
            insufficient_embed = discord.Embed(title="Insufficient Funds!", description=f"You only have {sender_acc['coins']} coins.\nYou are {amount - sender_acc['coins']} coins short!")
            await ctx.response.send_message(embed=insufficient_embed)
            return
        await self.db.update('accounts', {'coins': sender_acc['coins']-amount}, f'user_id = {ctx.user.id}')
        await self.db.update('accounts', {'coins': recipient_acc['coins']+amount}, f'user_id = {recipient.id}')

        success_embed = discord.Embed(title="Success!", description=f"You successfully sent {amount} coins to {recipient.mention}")
        success_embed.add_field(name="Your balance", value=f"{sender_acc['coins']-amount}")
        success_embed.add_field(name="Their balance", value=f"{recipient_acc['coins']+amount}")

        await ctx.response.send_message(embed=success_embed)


    @app_commands.command(name="rob")
    @app_commands.describe(user="The user you want to rob")
    @app_commands.checks.cooldown(1, 300)
    async def rob(
        self,
        ctx: discord.Interaction,
        user: discord.User
    ):
        if user.bot:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(user.id)))
            return  

        if user.id == ctx.user.id:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Whoops", "You can't rob yourself!"))
            return
            
        author_bal = await self.fetch_or_create_account(ctx.user)
        victim_bal = await self.fetch_or_create_account(user)

        if victim_bal['coins'] < 200:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Whoops", f"{user.mention} doesn't have enough coins to steal"))
            return

        luck = random.randint(65, 75)
        r_amt = random.randint(110, 500)

        if luck in (69, 70):
            await self.db.update('accounts', {'coins': victim_bal['coins']-r_amt}, f'user_id={user.id}')
            await self.db.update('accounts', {'coins': author_bal['coins']+r_amt}, f'user_id={ctx.user.id}')

            await ctx.response.send_message(embed=utils.Embed.SUCCESS(f"You robbed {user.mention}", f"You stole {r_amt} coins from {user.mention}"))

        else:
            await self.db.update('accounts', {'coins': author_bal['coins']-r_amt}, f'user_id={ctx.user.id}')
            
            await ctx.response.send_message(embed=utils.Embed.ERROR(f"You tried to rob {user.mention}", f"You got caught robbing {user.mention} and were fined {r_amt} coins"))


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
        utils.Column("theft_pings", bool),
        utils.Column("passive_mode", bool)
    ],
    primary_key="user_id"
)

async def setup(bot):
    await bot.add_cog(Economy(bot))
