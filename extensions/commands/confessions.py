from __future__ import annotations

import discord

from discord.ext import commands
from discord import app_commands

from utils.utils import Embed
from utils.db import Database, Table, Column


class Confessions(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database(
            "database/confessions.db", "confessions", tables=[confessions_table]
        )

    async def cog_load(self) -> None:
        await self.db.connect()

    async def cog_unload(self) -> None:
        await self.db.close()

    confessions = app_commands.Group(
        name="confessions", description="Post anonymous confessions"
    )

    @app_commands.command(name="setup", description="Setup Confession in your server.")
    @app_commands.describe(channel="The channel in which confessions will be posted.")
    async def setup(self, ctx: discord.Interaction, channel: discord.TextChannel):
        db = self.db
        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if data:
            return await ctx.response.send_message(
                embed=Embed.SUCCESS(
                    "Confessions is Already Setuped!",
                    f"Are you sure that you want to change the confession channel to: {channel.mention}. If Yes click the button below.",
                ),
                view="TBD",
            )

        perms = channel.permissions_for(ctx.guild.me)
        if (
            not perms.manage_channels
            and perms.read_message_history
            and perms.read_messages
            and perms.send_messages
            and perms.manage_messages
        ):
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "I Need Permissions!",
                    "I don't have the required permission in the channel.",
                )
            )

        await db.insert(
            "confessions",
            (ctx.guild_id, channel.id, "ENABLE", "ENABLE", "ENABLE", None),
        )
        embed = Embed(
            title="Setup Complete!",
            description=f"Now you can use confess anonymously in {channel.mention} using `/confess` command in the server.",
        )
        embed.add_field(
            name="HelpFul Tips To Manage Confessions:",
            value="`1.` Only Members with `Manage Server` permission can manage confessions\n\n"
            "`2.` If you want NSFW Free Confessions Enable NSFW Detection Feature by `/confessions detect_nsfw` command.\n\n"
            "`3.` You can also Enable Image Support for confessions using `/confessions img` command."
            "`4.` You can Temporarily Enable/Disable Confessions using `/confessions toggle` command.",
        )
        await ctx.response.send_message(embed=embed)


confessions_table = Table(
    "confessions",
    columns=[
        Column("guild_id", int),
        Column("channel_id", int),
        Column("toggle", str),
        Column("allow_img", str),
        Column("detect_nsfw", str),
        Column("blacklisted_users", str),
    ],
)


async def setup(bot):
    await bot.add_cog(Confessions(bot))
