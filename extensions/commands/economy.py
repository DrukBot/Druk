from datetime import datetime
import discord
import random
import utils
import typing
import json

from discord.ext import commands, tasks
from discord import app_commands
from discord.app_commands import Choice

from components import (
    paginator,
)

from utils.utils import Embed, log
from components.economy import RegisterUser, UserInventory, CoinflipChallenge


class Economy(commands.Cog):
    def __init__(self, bot):
        self.bot: commands.Bot = bot
        self.db: utils.Database = utils.Database("economy", [accounts_table, settings_table, user_stock_table])

    async def cog_load(self) -> None:
        await self.db.connect()
        self.connection_refresh.start()

    async def register_user(self, ctx: discord.Interaction, user: discord.User):
        if user.bot:
            return await ctx.response.send_message("Bots can't be registered!")
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")
        if acc:
            await ctx.response.send_message("You are already a registered user!", ephemeral=True)
            return

        embed = Embed(title="Breaking these rules can be resulting in ban/deletion/reset of you account.", description="RULES TO BE FOLLOWED").set_author(name="Druk Rules!", icon_url=self.bot.user.display_avatar.url)
        await ctx.response.send_message(embed=embed, view=RegisterUser(user, self.db))

    
    async def add_item(self, ctx: discord.Interaction, user: discord.User, name: str, description: str, value: int = None, amount: int = 1):
        acc = await self.get_user_account(ctx, user)
        if acc is None:
            return None
        inv = json.loads(acc['inventory'])
        try:
            inv[name]['amount'] += amount
            if value is not None:
                inv[name]['value'] = value
        except KeyError:
            inv[name] = {'description': description, 'amount': amount, 'value': value }
            finv = json.dumps(inv)
            await self.db.update('accounts', {'inventory': finv}, f"user_id = {user.id}")
            return True



    async def get_user_account(self, ctx: discord.Interaction, user: typing.Union[discord.User, discord.Member]):
        acc = await self.db.fetch('accounts', f"user_id = {user.id}")

        if acc:
            return acc
        else:
            return None


    async def get_user_settings(self, ctx: discord.Interaction, user: typing.Union[discord.User, discord.Member]):
        s = await self.db.fetch('settings', f"user_id = {user.id}")

        if s:
            return s
        embed = Embed(description=f"{user} is not a registered user.\n\nUse `/register` command to create you account.").set_author(name="User Not Registered!", icon_url=user.display_avatar.url)
        await ctx.response.send_message(embed=embed)


    @tasks.loop(minutes=5)
    async def connection_refresh(self):
        await self.db.close()
        sleep(5)
        await self.db.connect()
        await self.bot.log_webhook(embed=utils.Embed.SUCCESS("Complete", f"`drukeconomy` connection refreshed at <t:{round(datetime.now().timestamp())}:T>"))


    @connection_refresh.before_loop
    async def before_refresh(self):
        await self.bot.wait_until_ready()
    

    @app_commands.command(name="register")
    async def register(self, ctx: discord.Interaction):
        await self.register_user(ctx, ctx.user)
        

    @app_commands.command(name='work')
    @app_commands.checks.cooldown(1, 120)
    async def work(
        self,
        ctx: discord.Interaction,
    ):
        acc = await self.get_user_account(ctx, ctx.user)
        if acc is None:
            return await ctx.response.send_message("User is not registered!")
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
        if acc is None:
            return await ctx.response.send_message("User is not registered!")
        sa = await self.get_user_settings(ctx, user)
        if sa is None:
            return

        if sa["privacy"] is True and user != ctx.user:
            await ctx.response.send_message(f"**{user}** has his wallet private.", ephemeral=True)
        if user.bot:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah There", "<@{}> is a bot, you can't do that".format(user.id)), ephemeral=True)   

        coins, cash = acc['coins'], acc['cash']

        wE = discord.Embed(description="**Wallet**").set_author(name=user, icon_url=user.display_avatar.url)
        wE.add_field(name="Coins", value=coins)
        wE.add_field(name="Cash", value=cash)
        wE.set_footer(text=f"Requested by {ctx.user}")

        await ctx.response.send_message(embed=wE)


    @app_commands.command(name='leaderboard')
    async def leaderboard(
        self,
        ctx: discord.Interaction,
    ):
        accs = await self.db.fetch('accounts', all=True, order_by='coins DESC')
        pag = paginator.Paginator(page_size = 100 )
        for i, acc in enumerate(accs):
            mem = ctx.guild.get_member(acc['user_id'])
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
        if sa is None:
            return await ctx.response.send_message("User is not registered!")
        ra = await self.get_user_account(ctx, recipient)

        if sa['coins'] < amount:
            insufficient_embed = discord.Embed(title="Insufficient Funds!", description=f"You only have {sa['coins']} coins.\nYou are {amount - sa['coins']} coins short!")
            await ctx.response.send_message(embed=insufficient_embed)
            return
        await self.db.update('accounts', {'coins': sa['coins']-amount}, f'user_id = {ctx.user.id}')
        await self.db.update('accounts', {'coins': ra['coins']+amount}, f'user_id = {recipient.id}')

        se = Embed(description=f"Transfered `{amount}` Credits to **{recipient}** Account.").set_author(name=ctx.user, icon_url=ctx.user.display_avatar.url)

        await ctx.response.send_message(embed=se)

    @app_commands.command(name="remove")
    async def removeUser(self, ctx: discord.Interaction, user: discord.User = None):
        if ctx.user.id not in self.bot.owner_ids:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah there!", "You don't have permission to do that!"))
        if user is None:
            user = ctx.user

        acc = await self.get_user_account(ctx, user)
        if acc is None:
            return await ctx.response.send_message("User is not registered!")
        accSettings = await self.get_user_account(ctx, user)
        if accSettings is None:
            return
        
        await self.db.delete('accounts', f"user_id={user.id}")
        await self.db.delete('settings', f"user_id={user.id}")

        embed = utils.Embed.SUCCESS("Success!", f"{user.mention} has been removed from the database!\nThey had {acc['coins']} coins and {acc['cash']} cash")

        await ctx.response.send_message(embed=embed)


    @app_commands.command(name="list-stocks")
    async def listStocks(self, ctx: discord.Interaction):
        await ctx.response.defer()
        pag = commands.Paginator('', '', max_size=100)
        stocks = await self.db.fetch("stock_info", all=True)
        for i, stock in enumerate(stocks):
            pag.add_line(f"ID: {stock['stock_id']}\nDescription: {stock['name']}\nPrice: {stock['price']}\nRemaining: {stock['remaining']}")

        stock_embed = discord.Embed(title="Stocks", color=discord.Color.green(), description=pag.pages[0])
        view = paginator.PaginatorView(pag, ctx.user, embed=stock_embed)

        await ctx.edit_original_response(view=view, embed=stock_embed)


    @app_commands.command(name="buy-stock")
    async def buyStock(self, ctx: discord.Interaction):
        await ctx.response.defer()

        acc = self.get_user_account(ctx, ctx.user)
        if acc is None:
            return await ctx.response.send_message("User is not registered!")

        pag = commands.Paginator('', '', max_size=100)
        stocks = await self.db.fetch("stock_info", all=True)
        for i, stock in enumerate(stocks):
            pag.add_line(f"ID: {stock['stock_id']}\nDescription: {stock['name']}\nPrice: {stock['price']}\nRemaining: {stock['remaining']}")

        stock_embed = discord.Embed(title="Stocks", color=discord.Color.green(), description=pag.pages[0])
        view = paginator.BuyStockPaginatorView(pag, ctx.user, embed=stock_embed, cache=stocks, db=self.db)

        await ctx.edit_original_response(view=view, embed=stock_embed)

    @app_commands.command(name="inventory")
    async def inventory(self, ctx: discord.Interaction):
        await ctx.response.defer()

        user_inv = await self.get_user_account(ctx, ctx.user)
        if user_inv is None:
            return await ctx.edit_original_response(content="User is not registered!")
        if user_inv['inventory'] is None:
            return await ctx.edit_original_response(embed=utils.Embed.ERROR("Woah", "You do not have any items!"))
        items: object = json.loads(user_inv['inventory'])
        embed = utils.Embed(title="Inventory")
        for item, item_data in items.items():
            embed.add_field(name=item, value=f"Amount: {item_data['amount']}\nValue: {item_data['value']}", inline=False)

        await ctx.edit_original_response(embed=embed, view=UserInventory(ctx.user, self.db))

    
    @app_commands.command(name="testing-items")
    async def testingItems(self, ctx: discord.Interaction, name: str, description: str, value: int):
        if ctx.user.id not in self.bot.owner_ids:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Whoa", "You can't use this command, you aren't an owner"))
        
        resp = await self.add_item(ctx, ctx.user, name, description, value)

        if resp is None:
            await ctx.response.send_message(embed=utils.Embed.ERROR("Whoops", "Something went wrong trying to do that"))
        else:
            await ctx.response.send_message(embed=utils.Embed.SUCCESS("Success!", "The item {} with description {} was added successfully".format(name, description)))


    @app_commands.command(name="networth")
    async def networth(self, ctx: discord.Interaction, user: discord.User = None):
        return await ctx.response.send_message(embed=utils.Embed.ERROR("Whoops", "This command is disabled at the moment"))


        await ctx.response.defer()

        msg_content = None

        user = ctx.user or user
        acc = await self.get_user_account(ctx, user)
        if acc is None:
            return ctx.edit_original_response(content="User is not registered!")
        settings = await self.get_user_settings(ctx, user)

        if settings['privacy'] and ctx.user.id != user.id:
            return await ctx.edit_original_response(embed=utils.Embed.ERROR("Whoops", f"{user.mention} has their profile private!"))
        
        if settings['pings'] and ctx.user.id != user.id:
            msg_content = user.mention


    @app_commands.command(name="coinflip")
    @app_commands.choices(
        side=[
            Choice(name="Heads", value="Heads"),
            Choice(name="Tails", value="Tails")
        ]
    )
    async def coinflip(self, ctx: discord.Interaction, side: Choice[str], opponent: discord.User, bet: int):
        if opponent.bot:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah", "You can't go against a bot!"), ephemeral=True)

        acc = await self.get_user_account(ctx, ctx.user)
        if acc is None:
            return await ctx.response.send_message(f"{ctx.user.mention} is not registered!")
        acc_settings = await self.get_user_settings(ctx, ctx.user)
        op_acc = await self.get_user_account(ctx, opponent)
        if op_acc is None:
            return await ctx.response.send_message(f"{opponent.mention} is not registered!")
        op_acc_settings = await self.get_user_settings(ctx, opponent)
        if bet < 1:
            return await ctx.response.send_message(f"Woah there! You can't bet less than 1 coin")

        if acc['coins'] < bet:
            if acc_settings['pings']:
                return await ctx.response.send_message(f"Whoops, {ctx.user.mention} does not have enough coins for this")
            else:
                return await ctx.response.send_message(f"Whoops, {ctx.user} does not have enough coins for this")
        

        if op_acc['coins'] < bet:
            if op_acc_settings['pings']:
                return await ctx.response.send_message(f"Whoops, {opponent.mention} does not have enough coins for this")
            else:
                return await ctx.response.send_message(f"Whoops, {opponent} does not have enough coins for this")

        opponent_coin = "Heads" if side.value == "Tails" else "Tails"
        
        if op_acc_settings['pings']:
            embed = utils.Embed(title="Coinflip", description=f"{ctx.user.mention} has invited you to a duel")
            await ctx.response.send_message(content= opponent.mention, embed=embed, view=CoinflipChallenge(ctx.user, side.value, opponent, opponent_coin, bet, self.db))
        else:
            embed = utils.Embed(title="Coinflip", description=f"{ctx.user.mention} has invited you to a duel")
            await ctx.response.send_message(embed=embed, view=CoinflipChallenge(ctx.user, side.value, opponent, opponent_coin, bet, self.db))

        
        



accounts_table = utils.Table(
    "accounts",
    [
        utils.Column("user_id", int),
        utils.Column("coins", int),
        utils.Column("cash", int),
        utils.Column("inventory", "TEXT")
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

user_stock_table = utils.Table(
    "user_stocks",
    [
        utils.Column("user_id", int),
        utils.Column("total_owned", int),
        utils.Column("stocks", "TEXT")
    ],
    primary_key="user_id"
)

async def setup(bot):
    await bot.add_cog(Economy(bot))
