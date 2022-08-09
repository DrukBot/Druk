import discord

from typing import Optional
from discord.ext import commands
from discord import app_commands
from discord.app_commands import Choice


from utils.utils import Embed


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    moderation = app_commands.Group(
        name="moderation", description="Moderation commands for your server"
    )

    @moderation.command(
        name="slowmode", description="Sets the slowmode duration for the channel"
    )
    @app_commands.choices(
        measure=[
            Choice(name="seconds", value="seconds"),
            Choice(name="minutes", value="minutes"),
            Choice(name="hours", value="hours"),
        ]
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def slowmode(self, ctx: discord.Interaction, time: int, measure: Choice[str]):
        if time == 0:
            await ctx.channel.edit(slowmode_delay=time)
            embed = Embed(
                title="Slowmode Disabled",
                description="Slowmode has now been disabled in this channel",
            )
        else:
            if measure.value == "seconds":
                slowmode_seconds = time
            elif measure.value == "minutes":
                slowmode_seconds = time * 60
            elif measure.value == "hours":
                slowmode_seconds = time * 3600

            await ctx.channel.edit(slowmode_delay=slowmode_seconds)

            embed = Embed(
                title="Slowmode Enabled",
                description=f"Slowmode has been set to {time}{measure.name}",
            )

        await ctx.response.send_message(embed=embed)

    @moderation.command(name="lock", description="Locks the channel")
    @app_commands.describe(channel="The channel to lock")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def lock(self, ctx: discord.Interaction, channel: discord.TextChannel):
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)

            if overwrite.send_messages is False:
                return await ctx.response.send_message(
                    embed=Embed.ERROR("Error!", "This channel is already locked"),
                    ephemeral=True,
                )

            overwrite.send_messages = False
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.response.send_message(
                embed=Embed.SUCCESS("Success!", "This channel has been locked"),
                ephemeral=True,
            )
        except:
            await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!", "Its seems like i don't have permission to do that."
                ),
                ephemeral=True,
            )

    @moderation.command(name="unlock", description="Unlocks the channel")
    @app_commands.describe(channel="The channel to unlock")
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_channels=True)
    async def unlock(self, ctx: discord.Interaction, channel: discord.TextChannel):
        try:
            overwrite = channel.overwrites_for(ctx.guild.default_role)

            if overwrite.send_messages is True:
                return await ctx.response.send_message(
                    embed=Embed.ERROR("Error!", "This channel is already unlocked"),
                    ephemeral=True,
                )

            overwrite.send_messages = True
            await channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
            await ctx.response.send_message(
                embed=Embed.SUCCESS("Success!", "This channel has been unlocked"),
                ephemeral=True,
            )
        except:
            await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!", "Its seems like i don't have permission to do that."
                ),
                ephemeral=True,
            )

    @moderation.command(name="role-give", description="Gives a role to a member")
    @app_commands.describe(
        member="The member to give the role to", role="The role to give"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def giveRole(
        self, ctx: discord.Interaction, member: discord.Member, role: discord.Role
    ):
        if role >= ctx.user.top_role:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!",
                    "You cannot assign roles higher (or equal to) your own top role!",
                )
            )

        if not role.is_assignable():
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!", "I dont have permission to assign this role!"
                )
            )

        await member.add_roles(role)
        await ctx.response.send_message(
            embed=Embed.SUCCESS("Success!", "The role has been assigned to the member")
        )

    @moderation.command(name="role-remove", description="Removes a role from a member")
    @app_commands.describe(
        member="The member to remove the role from", role="The role to remove"
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def removeRole(
        self, ctx: discord.Interaction, member: discord.Member, role: discord.Role
    ):
        if role >= ctx.user.top_role:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!",
                    "You cannot assign roles higher (or equal to) your own top role!",
                )
            )

        if not role.is_assignable():
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!", "I dont have permission to assign this role!"
                )
            )

        await member.remove_roles(role)
        await ctx.response.send_message(
            embed=Embed.SUCCESS("Success!", "The role has been removed from the member")
        )

    @moderation.command(
        name="role-exchange", description="Exchanges a role for another"
    )
    @app_commands.describe(
        member="The member to exchange the role from",
        role_to_add="The role to add",
        role_to_remove="The role to remove",
    )
    @app_commands.guild_only()
    @app_commands.checks.has_permissions(manage_roles=True)
    async def roleExchange(
        self,
        ctx: discord.Interaction,
        member: discord.Member,
        role_to_add: discord.Role,
        role_to_remove: discord.Role,
    ):
        if role_to_add >= ctx.user.top_role or role_to_remove >= ctx.user.top_role:
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!",
                    "You cannot assign roles higher (or equal to) your own top role!",
                )
            )

        if not role_to_add.is_assignable() or role_to_remove.is_assignable():
            return await ctx.response.send_message(
                embed=Embed.ERROR(
                    "Error!", "I dont have permission to assign this role!"
                )
            )

        if role_to_add == role_to_remove:
            return await ctx.response.send_message(
                embed=Embed.ERROR("Error!", "You cannot exchange a role for itself!")
            )

        await member.add_roles(role_to_add)
        await member.remove_roles(role_to_remove)
        await ctx.response.send_message(
            embed=Embed.SUCCESS("Success!", "The role has been exchanged")
        )


async def setup(bot):
    await bot.add_cog(Moderation(bot))
