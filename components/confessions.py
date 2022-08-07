import discord


from typing import Optional

from utils.utils import Embed


class ChangeChannel(discord.ui.View):
    def __init__(self, db, channel):
        super().__init__(timeout=30)
        self.db = db
        self.channel = channel

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.button):
        try:
            await self.db.execute("UPDATE confessions SET channel_id = ? WHERE guild_id = ?", (self.channel.id, ctx.guild_id))
            await self.db.commit()
        except Exception as e:
            print(e)

        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                "Updated Confession Channel!",
                f"{self.channel.mention} is now configured as confession channel.",
            )
        )

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


class SendConfession(discord.ui.Modal, title="Send Confession"):
    content = discord.ui.TextInput(
        label="Confession",
        placeholder="Enter your confession here",
        style=discord.TextStyle.paragraph,
        required=True,
        min_length=25,
        max_length=4000,
    )

    def __init__(self, db, channel: discord.TextChannel, image: Optional[str] = None):
        super().__init__()
        self.db = db
        self.channel = channel
        self.image = image

    async def on_submit(self, ctx: discord.Interaction):
        channel = self.channel
        content = self.content.value
        image_url = self.image

        embed = Embed(description=content, color=discord.Color.random())
        embed.set_author(name="Anonymous Confession")
        if image_url:
            embed.set_image(url=image_url)

        await channel.send(embed=embed)
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                "Confession Sent!", "You anonymous confession has been sent."
            ),
            ephemeral=True,
        )
