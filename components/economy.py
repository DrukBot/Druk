import discord
import utils
import json
import random


class RegisterUser(discord.ui.View):
    def __init__(self, user: discord.User, db):
        super().__init__(timeout=30)
        self.user = user
        self.db = db

    @discord.ui.button(label="I Accept the rule!", style=discord.ButtonStyle.green)
    async def callback(self, ctx: discord.Interaction, button: discord.ui.Button):
        acc = await self.db.fetch('accounts', f"user_id = {self.user.id}")
        if acc:
            await ctx.response.send_message("You are already a registered user!", ephemeral=True)
            return

        await self.db.insert('accounts', (self.user.id, 500, 0))
        await self.db.insert('settings', (self.user.id, True, False))
        embed = utils.Embed(description="Successfully registered your account!").set_author(name="User Registered!", icon_url=self.user.display_avatar.url)
        button.disabled = True
        await ctx.response.edit_message(embed=embed, view=None)

    async def interaction_check(self, ctx: discord.Interaction) -> bool:
        if ctx.user.id != self.user.id:
            await ctx.response.send_message("You can not perform this action.")
        else:
            return True



class UserInventory(discord.ui.View):
    def __init__(self, user: discord.User, db: utils.Database):
        super().__init__(timeout=60)
        self.user = user
        self.db = db

    @discord.ui.button(label="Value", style=discord.ButtonStyle.green, custom_id="enabled")
    async def value(self, ctx: discord.Interaction, button: discord.ui.Button):
        account = await self.db.fetch('accounts', f"user_id = {self.user.id}")
        items: object = json.loads(account['inventory'])
        embed = utils.Embed(title="Inventory")

        if self.value.custom_id == "enabled":
            self.value.custom_id = "disabled"
            self.value.style = discord.ButtonStyle.red
            for item, item_data in items.items():
                embed.add_field(name=item, value=f"Amount: {item_data['amount']}", inline=False)
            await ctx.response.edit_message(embed=embed, view=self)
        elif self.value.custom_id == "disabled":
            self.value.custom_id = "enabled"
            self.value.style = discord.ButtonStyle.green
            for item, item_data in items.items():
                embed.add_field(name=item, value=f"Amount: {item_data['amount']}\nValue: {item_data['value']}", inline=False)
            await ctx.response.edit_message(embed=embed, view=self)


class CoinflipChallenge(discord.ui.View):
    def __init__(self, challenger: discord.User, c_coin: str, opponent: discord.User, op_coin: str, bet: int, db: utils.Database):
        super().__init__(timeout=300)
        self.challenger = challenger
        self.challenger_coin = c_coin
        self.opponent = opponent
        self.op_coin = op_coin
        self.bet = bet
        self.db = db

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept_cf(self, ctx: discord.Interaction, button: discord.ui.Button):
        if ctx.user.id != self.opponent.id:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah", "You can't use this!"), ephemeral=True)
        await ctx.response.defer()
        result = random.choice(['Heads', 'Tails'])
        content: str
        if result == self.challenger_coin:
            embed = discord.Embed(title="Result", color=discord.Color.blurple())
            challenger_pings = await self.db.fetch('settings', f"user_id={self.challenger.id}")
            challenger_pings = challenger_pings['pings']
            embed.add_field(name="Challenger", value=f"Congrats {self.challenger.mention}, you won {self.bet} coins")
            content = f"{self.challenger.mention if challenger_pings else None}"
            opponent_pings = await self.db.fetch('settings', f"user_id={self.opponent.id}")
            opponent_pings = opponent_pings['pings']
            embed.add_field(name="Opponent", value=f"Oh no! {self.opponent.mention if opponent_pings else self.opponent} you lost {self.bet} coins")
            content += f"{self.opponent.mention if opponent_pings else None}"
            challenger = await self.db.fetch('accounts', f"user_id={self.challenger.id}")
            await self.db.update('accounts', {'coins': challenger['coins']+self.bet}, f"user_id={self.challenger.id}")
            opponent = await self.db.fetch('accounts', f"user_id={self.opponent.id}")
            await self.db.update('accounts', {'coins': opponent['coins']-self.bet}, f"user_id={self.opponent.id}")

            await ctx.response.send_message(content = content)
            return await ctx.response.edit_message(content=None, embed=embed, view=None)
    
    @discord.ui.button(label="Deny", style=discord.ButtonStyle.red)
    async def deny_cf(self, ctx: discord.Interaction, button: discord.ui.Button):
        if ctx.user.id != self.opponent.id:
            return await ctx.response.send_message(embed=utils.Embed.ERROR("Woah", "You can't use this!"), ephemeral=True)
        challenger_pings = await self.db.fetch('settings', f"user_id={self.challenger.id}")
        challenger_pings = challenger_pings['pings']
        embed = discord.Embed(title="Coinflip Declined!", description=f"{self.opponent.mention} declined your coinflip!")
        if challenger_pings:
            content = f"{self.challenger.mention}"
        else:
            content = None

        await ctx.response.edit_message(embed=embed, view=None)
        return await ctx.response.send_message(content = content)