import discord


from utils.utils import Embed, COLOURS


class ChangeChannel(discord.ui.View):
    def __init__(self, db, channel):
        super().__init__(timeout=30)
        self.db = db
        self.channel = channel
        self.message = None

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, ctx: discord.Interaction, button: discord.ui.button):
        await self.db.execute(
            "UPDATE report SET channel_id = ? WHERE guild_id = ?",
            (self.channel.id, ctx.guild_id),
        )
        await self.db.commit()

        self.clear_items()
        await ctx.response.edit_message(
            embed=Embed.SUCCESS(
                "Updated Report System Channel!",
                f"{self.channel.mention} is now configured as rpeorting channel.",
            ), view=self
        )

    async def interaction_check(self, ctx: discord.Interaction):
        if not ctx.user.guild_permissions.manage_guild:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "You Can't do that",
                    "You don't have required permission to perform that action.",
                ), ephemeral=True
            )
        else:
            return True


class SubmitReport(discord.ui.Modal, title="Submit Report"):
    content = discord.ui.TextInput(
        label="Report Content:",
        placeholder="Report Content here...",
        style=discord.TextStyle.paragraph,
        min_length=25,
        max_length=4000,
        required=True,
    )

    def __init__(self, channel: discord.TextChannel, role, thread, proof, anon):
        super().__init__()
        self.channel = channel
        self.role = role
        self.thread = thread
        self.proof = proof
        self.anon = anon

    async def on_submit(self, ctx: discord.Interaction):
        embed = Embed(timestamp=discord.utils.utcnow(), description=self.content.value)

        if not self.anon:
            embed.set_author(
                name=f"{ctx.user} | Report",
                icon_url=(ctx.user.avatar or ctx.user.default_avatar).url,
            )
        else:
            embed.set_author(name="Anonymous Report")

        if self.proof:
            embed.set_image(url=self.proof)

        msg = await self.channel.send(
            content=self.role.mention if self.role else None,
            embed=embed,
            allowed_mentions=discord.AllowedMentions(roles=True),
            view=ReportAction(),
        )

        await ctx.response.send_message(
            embed=Embed.SUCCESS("Report Sent!", "Your report has been sent."), ephemeral=True
        )

        if self.thread:
            await msg.create_thread(
                name=f"Report From {ctx.user}", reason=f"New Report From {ctx.user}"
            )


class ReportAction(discord.ui.View):
    def __init__(self):
        super().__init__()

    @discord.ui.button(
        label="Mark As Solved", style=discord.ButtonStyle.green, custom_id="solve"
    )
    async def solved_callback(
        self, ctx: discord.Interaction, button: discord.ui.button
    ):
        embed = ctx.message.embeds[0]
        embed.color = COLOURS.green
        embed.add_field(name="Status", value="**Report Solved**", inline=False)
        self.clear_items()
        await ctx.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Spam Report", style=discord.ButtonStyle.red, custom_id="spam"
    )
    async def spam_callback(self, ctx: discord.Interaction, button: discord.ui.button):
        embed = ctx.message.embeds[0]
        embed.color = COLOURS.red
        embed.add_field(name="Status", value="**Report Spam**", inline=False)
        self.clear_items()
        await ctx.response.edit_message(embed=embed, view=self)

    @discord.ui.button(
        label="Pin Report", style=discord.ButtonStyle.blurple, custom_id="pin"
    )
    async def pin(self, ctx: discord.Interaction, button: discord.ui.button):
        await ctx.message.pin(reason=f"Report Pinned By: {ctx.user}")
        for i in self.children:
            if i.custom_id == "pin":
                i.disable = True
        await ctx.message.edit(view=self)
        await ctx.response.send_message(
            embed=Embed.SUCCESS("Pinned!", "Successfully pinned report, check pins!"),
            ephemeral=True,
        )
