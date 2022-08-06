import discord


from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice

from utils.utils import Embed
from components.report import SubmitReport, ChangeChannel
from utils.db import Database, Table, Column


class Report(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.db = Database("database/report.db", "report", tables=[report_table])

    async def cog_load(self) -> None:
        await self.db.connect()

    async def cog_unload(self) -> None:
        await self.db.close()

    @staticmethod
    async def get_channel(ctx: discord.Interaction, channel_id: int):
        channel = ctx.guild.get_channel(channel_id)

        if channel is None:
            return await ctx.response.send_message(
                embed=Embed.ERROR("Error!", "Unable To Fetch Report System Channel."),
                ephemeral=True,
            )
        else:
            return channel

    @staticmethod
    async def get_role(ctx: discord.Interaction, role_id):
        if role_id is None:
            return None

        role = ctx.guild.get_role(role_id)

        if role is None:
            return await ctx.response.send_message(
                embed=Embed.ERROR("Error", "Unable To Fetch Report System Ping Role"),
                ephemeral=True,
            )
        else:
            return role

    reportconfig = app_commands.Group(
        name="reportconfig", description="Configure the reports."
    )

    @reportconfig.command(
        name="setup", description="Setup the report system in your server."
    )
    @app_commands.describe(channel="The channel in which reports will be posted.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setup(self, ctx: discord.Interaction, channel: discord.TextChannel):
        db = self.db
        data = await db.select("report", f"guild_id = {ctx.guild_id}")

        if data:
            view = ChangeChannel(self.db, channel)
            view.message = await ctx.response.send_message(
                embed=Embed.SUCCESS(
                    "Report System is Already Setuped!",
                    f"Are you sure that you want to change the report channel to: {channel.mention}. If Yes click the button below.",
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

        await db.insert("report", (ctx.guild_id, channel.id, None, "ENABLE", "ENABLE"))

        embed = Embed(
            title="Report System Setuped!",
            description=f"The report channel is now {channel.mention}.",
        )
        embed.add_field(
            name="Helpfull Tips to manage the report system.",
            value="`1.` Only Member with `Manage Server` permission can manage the report system.\n\n"
            "`2.` Toggle Report system with `/reportconfig toggle` command."
            "`3.` Toggle Thread Support for Report system with `/reportconfig thread` command.",
            inline=False,
        )
        await ctx.response.send_message(embed=embed)

    @reportconfig.command(
        name="role", description="Setup the ping role for the report system."
    )
    @app_commands.describe(role="The role that will be pinged when a report is made.")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def role(self, ctx: discord.Interaction, role: discord.Role):
        db = self.db
        data = await db.select("report", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is Not Setuped!",
                    "You need to setup the report system first.",
                )
            )

        await db.update("report", {"role_id": role.id}, f"guild_id = {ctx.guild_id}")
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                "Ping Role Setuped!",
                f"The ping role for report system is now {role.mention}",
            )
        )

    @reportconfig.command(
        name="toggle", description="Toggle the report system in your server."
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[Choice(name="Enable", value="ENABLE"), Choice(name="Disable", value="DISABLE")]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.select("report", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setuped!",
                    "Please setup the report system first.",
                )
            )

        await db.update("report", {"toggle": mode.value}, f"guild_id = {ctx.guild_id}")
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Report System!", f"The report system is now {mode.name}."
            )
        )

    @reportconfig.command(
        name="thread",
        description="Toggle the Thread Support for report system in your server.",
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[Choice(name="Enable", value="ENABLE"), Choice(name="Disable", value="DISABLE")]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def thread(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.select("report", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setuped!",
                    "Please setup the report system first.",
                )
            )

        await db.update(
            "report", {"thread_support": mode.value}, f"guild_id = {ctx.guild_id}"
        )
        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Thread Support!",
                f"The thread support is now {mode.name} for report system.",
            )
        )

    @app_commands.command(name="report", description="Report a user in your server.")
    @app_commands.describe(
        anon="Wheather to send report anonymously or not",
        proof="Attach a image for a proof.",
    )
    @app_commands.choices(anon=[Choice(name="Yes", value="YES"), Choice(name="No", value="NO")])
    @app_commands.guild_only()
    async def report(
        self,
        ctx: discord.Interaction,
        anon: Choice[bool],
        proof: Optional[discord.Attachment] = None,
    ):
        db = self.db
        data = await db.select("report", f"guild_id = {ctx.guild_id}")

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setuped!",
                    "Please setup the report system first.",
                )
            )

        if data[3] == "DISABLE":
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is Disabled!",
                    "Report System is Disabled in this server.",
                )
            )

        role = self.get_role(data[2])
        channel = self.get_channel(int(data[1]))

        if data[4] == "ENABLE":
            threadSupport = True
        else:
            threadSupport = False
        
        if anon.value == "YES":
            anon = True
        else:
            anon = False

        await ctx.response.send_modal(
            SubmitReport(
                channel, role, threadSupport, proof.url if proof else None, anon
            )
        )


report_table = Table(
    "report",
    columns=[
        Column("guild_id", int),
        Column("channel_id", int),
        Column("role_id", int),
        Column("toggle", str),
        Column("thread_support", str),
    ],
)


async def setup(bot):
    await bot.add_cog(Report(bot))
