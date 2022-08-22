import discord
import typing
import utils
from discord.ext import commands


class Paginator:
    def __init__(self, prefix = '', suffix = '', sep = '\n', page_size = 300):
        self.page_size = page_size
        self.pages = ['']
        self.prefix = prefix
        self.suffix = suffix
        self.sep = sep

    def __len__(self) -> int:
        return self.pages

    def add_line(self, line: typing.Optional[str]):
        ll = len(line)
        if ll > self.page_size:
            raise ValueError(f'Line is too long! Expected less than {ll} characters.')
        if len(self.pages[-1]) + ll > self.page_size:
            self.pages.append('')
        self.pages[-1] += self.prefix + line + self.suffix + self.sep


class PaginatorView(discord.ui.View):
    def __init__(
        self,
        paginator,
        author: typing.Union[discord.User, discord.Member],
        **kwargs
    ):
        super().__init__(
            timeout = 30
        )
        self.paginator: Paginator = paginator
        self.author: typing.Union[discord.User, discord.Member] = author
        self.pages: int = len(paginator.pages)
        self.page: int = 1
        self.embed: discord.Embed = kwargs.pop("embed", None)
        if not self.embed:
            self.embed = discord.Embed(colour = discord.Color.red())
        self._original_embed_title = self.embed.title
        self.embed.title = f"{self._original_embed_title} [{self.page}/{self.pages}]"

    async def update_message(self, interaction: discord.Interaction):
        self.page_number.label = self.page + 1
        self.embed.title = f'{self._original_embed_title} [{self.page+1}/{self.pages}]'
        self.embed.description = self.paginator.pages[self.page]
        await interaction.response.edit_message(embed = self.embed, view = self)

    #Buttons

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "⏮️")
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        self.page = 0
        await self.update_message(interaction)

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "◀️")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        if self.page != 0:
            self.page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label = 1, style = discord.ButtonStyle.primary, disabled=True)
    async def page_number(self, interaction: discord.Interaction, button: discord.ui.Button):
        return

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "▶️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        page = self.page
        if page != self.pages:
            self.page += 1
        await self.update_message(interaction)

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "⏭️")
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        self.page = self.pages - 1
        await self.update_message(interaction)


class BuyStockPaginatorView(discord.ui.View):
    def __init__(
        self,
        paginator,
        author: typing.Union[discord.User, discord.Member],
        db: utils.Database,
        cache,
        **kwargs
    ):
        super().__init__(
            timeout = 30
        ),
        self.paginator: Paginator = paginator
        self.author: typing.Union[discord.User, discord.Member] = author
        self.pages: int = len(paginator.pages)
        self.page: int = 1
        self.embed: discord.Embed = kwargs.pop("embed", None)
        if not self.embed:
            self.embed = discord.Embed(colour = discord.Color.red())
        self._original_embed_title = self.embed.title
        self.embed.title = f"{self._original_embed_title} [{self.page}/{self.pages}]"
        self.db = db
        self.cache = cache

    def generate_uid(self, buyer: discord.User, stock):

        return f"{buyer.id}_{stock['stock_id']}"

    async def update_message(self, interaction: discord.Interaction):
        self.embed.title = f'{self._original_embed_title} [{self.page}/{self.pages}]'
        self.embed.description = self.paginator.pages[self.page]
        await interaction.response.edit_message(embed = self.embed, view = self)

    #Buttons

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "⏮️")
    async def first_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        self.page = 1
        await self.update_message(interaction)

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "◀️")
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        if self.page != 0:
            self.page -= 1
        await self.update_message(interaction)

    @discord.ui.button(label = "Select", style = discord.ButtonStyle.green)
    async def page_number(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.defer()
        userStocks = await self.db.fetch("user_stocks", f"user_id={interaction.user.id} AND stock_id='{list(enumerate(self.cache))[self.page][1]['stock_id']}'")
        userProfile = await self.db.fetch("accounts", f"user_id={interaction.user.id}")
        stockGrab = await self.db.fetch("stock_info", f"stock_id='{list(enumerate(self.cache))[self.page][1]['stock_id']}'")
        if userProfile['coins'] < stockGrab['price']:
            return await interaction.edit_original_response(embed=discord.Embed(title="Oh no!", description=f"You don't have enough to buy {stockGrab['stock_id']}. You need {stockGrab['price']}"), view=None)
        if userStocks is None:
            await self.db.insert("user_stocks", (self.generate_uid(interaction.user, stockGrab), interaction.user.id, stockGrab['stock_id'], 1))
            await self.db.update("stock_info", {"remaining": stockGrab['remaining']-1}, f"stock_id='{stockGrab['stock_id']}'")
        else:
            await self.db.update("user_stocks", {'total_owned': userStocks['total_owned']+1}, f"user_id={interaction.user.id} AND stock_id='{stockGrab['stock_id']}'")
            stockGrab = await self.db.fetch("stock_info", f"stock_id={list(enumerate(self.cache))[self.page][1]['stock_id']}")
            await self.db.update("stock_info", {'remaining': stockGrab['remaining']-1}, f"stock_id='{stockGrab['stock_id']}'")
        return await interaction.edit_original_response(embed=discord.Embed(title="Success!", description=f"You successfully bought 1 {stockGrab['stock_id']}\nThere are {stockGrab['remaining']-1} of these stocks remaining.", colour=discord.Color.green()), view=None)
        
            

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "▶️")
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        page = self.page
        if page != self.pages:
            self.page += 1
        await self.update_message(interaction)

    @discord.ui.button(style = discord.ButtonStyle.secondary, emoji = "⏭️")
    async def last_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author.id:
            return await interaction.response.send_message("This is not for you", ephemeral = True)
        self.page = self.pages - 1
        await self.update_message(interaction)