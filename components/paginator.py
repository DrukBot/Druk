import discord
import typing
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
