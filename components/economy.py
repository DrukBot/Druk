import discord
import utils


class RegisterUser(discord.ui.View):
    def __init__(self, user: discord.User, db):
        super().__init__(timeout=30)
        self.user = user
        self.db = db
        self.message = None

    @discord.ui.button(label="I Accept the rule!", style=discord.ButtonStyle.green)
    async def callback(self, ctx: discord.Interaction, button: discord.ui.button):
        acc = await self.db.fetch('accounts', f"user_id = {self.user.id}")
        if acc:
            await ctx.response.send_message("You are already a registered user!", ephemeral=True)
            return

        await self.db.insert('accounts', (self.user.id, 500, 0))
        await self.db.insert('settings', (self.user.id, False))
        embed = utils.Embed(description="Successfully registered your account!").set_author(name="User Registered!", icon_url=self.user.display_avatar.url)
        await ctx.response.send_message(embed=embed, ephemeral=True)

    async def interaction_check(self, ctx: discord.Interaction) -> bool:
        if ctx.user.id != self.user.id:
            await ctx.response.send_message("You can not perform this action.")

    async def on_timeout(self) -> None:
        for child in self.children:
            child.disabled = True

        await self.message.edit(view=self)

