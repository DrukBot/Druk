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
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if data:
            view = ChangeChannel(self.db, channel)
            view.message = await ctx.response.send_message(
                embed=Embed.SUCCESS(
                    "Report System is Already Setup!",
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
                ),
                ephemeral=True,
            )

        await db.insert("report", (ctx.guild_id, channel.id, None, "ENABLE", "ENABLE"))

        embed = Embed(
            title="Report System Setup!",
            description=f"The report channel is now {channel.mention}.",
        )
        embed.add_field(
            name="Helpfull Tips to manage the report system.",
            value="`1.` Only Member with `Manage Server` permission can manage the report system.\n\n"
            "`2.` Toggle Report system with `/reportconfig toggle` command.\n\n"
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
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is Not Setup!",
                    "You need to setup the report system first.",
                ),
                ephemeral=True,
            )

        await db.execute(
            "UPDATE report SET role_id = ? WHERE guild_id = ?", (role.id, ctx.guild_id)
        )
        await db.commit()

        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                "Ping Role Setup!",
                f"The ping role for report system is now {role.mention}",
            ),
            ephemeral=True,
        )

    @reportconfig.command(
        name="toggle", description="Toggle the report system in your server."
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[
            Choice(name="Enable", value="ENABLE"),
            Choice(name="Disable", value="DISABLE"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def toggle(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setup!",
                    "Please setup the report system first.",
                ),
                ephemeral=True,
            )

        await db.execute(
            "UPDATE report SET toggle = ? WHERE guild_id = ?",
            (mode.value, ctx.guild_id),
        )
        await db.commit()

        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Report System!", f"The report system is now {mode.name}."
            ),
            ephemeral=True,
        )

    @reportconfig.command(
        name="thread",
        description="Toggle the Thread Support for report system in your server.",
    )
    @app_commands.describe(mode="Choose a option")
    @app_commands.choices(
        mode=[
            Choice(name="Enable", value="ENABLE"),
            Choice(name="Disable", value="DISABLE"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def thread(self, ctx: discord.Interaction, mode: Choice[str]):
        db = self.db
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setup!",
                    "Please setup the report system first.",
                ),
                ephemeral=True,
            )

        await db.execute(
            "UPDATE report SET thread_support = ? WHERE guild_id = ?",
            (mode.value, ctx.guild_id),
        )
        await db.commit()

        await ctx.response.send_message(
            embed=Embed.SUCCESS(
                f"{mode.name} Thread Support!",
                f"The thread support is now {mode.name} for report system.",
            ),
            ephemeral=True,
        )

    @reportconfig.command(
        name="settings", description="View the settings for the report system."
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_guild=True)
    async def setttings(self, ctx: discord.Interaction):
        db = self.db
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setup!",
                    "Please setup the report system first.",
                ),
                ephemeral=True,
            )

        channel = await self.get_channel(ctx, int(data[1]))
        role = await self.get_role(ctx, data[2])
        mention_role = role.mention if role else "**Not Set**"
        toggle = data[3]
        thread_support = data[4]

        embed = Embed(
            title="Report System Settings",
            description="Druk's Report System Help server member's to contanct their problems with mods through Report System.\n\n"
            "Only Members with `Manage Server` permission can manage the report system.\n\n"
            f"This feature is currently **{toggle}**\n"
            "*Toggle this feature with `/reportconfig toggle` command.*",
        )

        embed.add_field(
            name="Channel",
            value=f"{channel.mention}\n"
            "*You can update report system channel with `/reportconfig setup` command.*",
            inline=False,
        )
        embed.add_field(
            name="Ping Role",
            value=f"{mention_role}\n"
            "*You can update ping role with `/reportconfig role` command.*",
            inline=False,
        )
        embed.add_field(
            name="Thread Support",
            value=f"**{thread_support}**\n"
            "*You can update thread support with `/reportconfig thread` command.*",
            inline=False,
        )

        await ctx.response.send_message(embed=embed)

    @app_commands.command(name="report", description="Report a user in your server.")
    @app_commands.describe(
        anon="Wheather to send report anonymously or not",
        proof="Attach a image for a proof.",
    )
    @app_commands.choices(
        anon=[Choice(name="Yes", value="YES"), Choice(name="No", value="NO")]
    )
    @app_commands.guild_only()
    async def report(
        self,
        ctx: discord.Interaction,
        anon: Choice[str],
        proof: Optional[discord.Attachment] = None,
    ):
        db = self.db
        data = await db.execute(
            "SELECT * FROM report WHERE guild_id = ?", (ctx.guild_id,)
        )

        if not data:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is not Setup!",
                    "Please setup the report system first.",
                ),
                ephemeral=True,
            )

        if data[3] == "DISABLE":
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Report System is Disabled!",
                    "Report System is Disabled in this server.",
                ),
                ephemeral=True,
            )

        try:

            role = await self.get_role(ctx, data[2])
            channel = await self.get_channel(ctx, int(data[1]))

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
        except Exception as e:
            print(e)


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
