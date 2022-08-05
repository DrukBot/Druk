from __future__ import annotations

import discord
import aiohttp

from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from utils.utils import Embed
from components.confessions import ChangeChannel, SendConfession
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

    @staticmethod
    async def detectNSFW(image_url: str):
        url = "https://nsfw-image-classification1.p.rapidapi.com/img/nsfw"
        payload = '{"url": "' + image_url + '"}'
        headers = {
            "content-type": "application/json",
            "x-rapidapi-key": "key",
            "x-rapidapi-host": "nsfw-image-classification1.p.rapidapi.com",
        }

        async with aiohttp.ClientSession() as session:
            response = await session.post(url, data=payload, headers=headers)

        if response.status == 200:
            json = await response.json()
            if round(json["NSFW_Prob"]) == 1:
                return True
            elif round(json["NSFW_Prob"]) == 0:
                return False
            else:
                return False

        else:
            return False

    confessions = app_commands.Group(
        name="confessions", description="Post anonymous confessions"
    )

    @confessions.command(name="setup", description="Setup Confession in your server.")
    @app_commands.describe(channel="The channel in which confessions will be posted.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx: discord.Interaction, channel: discord.TextChannel):
        db = self.db
        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if data:
            view = ChangeChannel(self.db, channel)
            view.message = await ctx.response.send_message(
                embed=Embed.SUCCESS(
                    "Confessions is Already Setuped!",
                    f"Are you sure that you want to change the confession channel to: {channel.mention}. If Yes click the button below.",
                ),
                view=view,
            )
            return

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
            title="<:success:1004762059981983754> Setup Complete!",
            description=f"Now you can use confess anonymously in {channel.mention} using `/confess` command in the server.",
        )
        embed.add_field(
            name="HelpFul Tips To Manage Confessions:",
            value="`1.` Only Members with `Manage Server` permission can manage confessions\n\n"
            "`2.` If you want NSFW Free Confessions Enable NSFW Detection Feature by `/confessions detect_nsfw` command.\n\n"
            "`3.` You can also Enable Image Support for confessions using `/confessions img` command.\n\n"
            "`4.` You can Temporarily Enable/Disable Confessions using `/confessions toggle` command.",
            inline=False,
        )
        await ctx.response.send_message(embed=embed)

    @confessions.command(
        name="toggle", description="Toggle the confessions in your server"
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[
            Choice(name="Enable", value="ENABLE"),
            Choice(name="Disbale", value="DISABLE"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Not Setuped!",
                    "Confessions are not setuped in this server.\n\nUse `/confessions setup` command to setup confessions.",
                )
            )

        await db.update(
            "confessions", {"toggle": mode.value}, f"guild_id = {ctx.guild_id}"
        )
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Confessions!",
                f"Successfully {mode.name} confessions in this server.",
            )
        )

    @confessions.command(
        name="detectnsfw", description="Toggle NSFW Detection feature for Confessions."
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[
            Choice(name="Enable", value="ENABLE"),
            Choice(name="Disbale", value="DISABLE"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def detectnsfw(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Not Setuped!",
                    "Confessions are not setuped in this server.\n\nUse `/confessions setup` command to setup confessions.",
                )
            )

        await db.update(
            "confessions", {"detect_nsfw": mode.value}, f"guild_id = {ctx.guild_id}"
        )
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} NSFW Detection!",
                f"Successfully {mode.name} NSFW content detection for confessions in this server.",
            )
        )

    @confessions.command(
        name="image_support",
        description="Toggle Image Support feature for Confessions.",
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[
            Choice(name="Enable", value="ENABLE"),
            Choice(name="Disbale", value="DISABLE"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def image_support(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Not Setuped!",
                    "Confessions are not setuped in this server.\n\nUse `/confessions setup` command to setup confessions.",
                )
            )

        await db.update(
            "confessions", {"allow_img": mode.value}, f"guild_id = {ctx.guild_id}"
        )
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Image Support!",
                f"Successfully {mode.name} Image Support for confessions in this server.",
            )
        )

    @app_commands.command(name="confess", description="Post anonymous confessions")
    @app_commands.describe(image="The image to be posted.")
    async def confess(
        self, ctx: discord.Interaction, image: Optional[discord.Attachment] = None
    ):
        db = self.db

        data = await db.select("confessions", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Not Setuped!",
                    "Confessions are not setuped in this server.\n\nUse `/confessions setup` command to setup confessions.",
                ),
                ephemeral=True,
            )

        if data[2] == "DISABLE":
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Disabled!", "Confessions are disabled in this server."
                ),
                ephemeral=True,
            )

        if data[3] == "DISABLE" and image is not None:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Image Support Disabled!",
                    "Image support for confessions is disabled in this server.",
                ),
                ephemeral=True,
            )

        if data[4] == "ENABLE" and image is not None:
            detect = self.detectNSFW(image.url)
            if detect:
                return await ctx.response.send_message(
                    embed=Embed.ERROR(
                        "NSFW Detected!", "NSFW content detected in the image."
                    )
                )
            else:
                pass

        image_url = image.url if image is not None else None
        channel = ctx.guild.get_channel(int(data[1]))
        if channel is None:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Confessions Channel Not Found!",
                    "Confessions channel is not found in this server. The channel is invalid or maybe deleted.",
                )
            )
        await ctx.response.send_modal(SendConfession(db, channel, image_url))


confessions_table = Table(
    "confessions",
    columns=[
        Column("guild_id", int),  # 0
        Column("channel_id", int),  # 1
        Column("toggle", str),  # 2
        Column("allow_img", str),  # 3
        Column("detect_nsfw", str),  # 4
        Column("blacklisted_users", str),  # 5
    ],
)


async def setup(bot):
    await bot.add_cog(Confessions(bot))
