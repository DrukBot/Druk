import discord


from utils.utils import Embed


class ChangeChannel(discord.ui.View):
    def __init__(self, db, channel):
        super().__init__(timeout=30)
        self.db = db
        self.channel = channel
        self.message = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.button):
        await self.db.update(
            "confessions",
            {"channel_id" : self.channel.id},
            f"guild_id = {ctx.guild_id}",
        )
        await ctx.response.send_message(embed=Embed.SUCCESS("Updated Confession Channel!", f"{self.channel.mention} is now configured as confession channel."))

    async def interaction_check(self, ctx: discord.Interaction):
        if not ctx.user.guild_permissions.manage_guild:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "You Can't do that",
                    "You don't have required permission to perform that action.",
                )
            )
        else:
            return True

    async def on_timeout(self):
        for view in self.children:
            view.disable = True

        await self.message.edit(view=self)
