from __future__ import annotations

import re
import traceback

import discord
from discord.ext import commands

from utils.objects import BaseEmbed
from utils.views import Traceback


class ErrorHandler(commands.Cog):
    """Universal error handler"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx: commands.Context, error: commands.CommandError) -> discord.Message:
        if hasattr(ctx.command, "on_error"):
            return
        error = getattr(error, "original", error)
        embed = BaseEmbed(
            title=f'Discord Error: {" ".join(re.split("(?=[A-Z])", type(error).__name__))}',
            color=0x800000,
        )
        if isinstance(error, commands.MissingPermissions):
            missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
            embed.description = "You are missing the following permissions required for this command:\n"
            for perm in missing:
                embed.description += f"**- {perm}**\n"
        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
            embed.description = "I am missing the following permissions required for this command:\n"
            for perm in missing:
                embed.description += f"**- {perm}**\n"
        elif isinstance(error, commands.MissingRequiredArgument):
            embed.description = f"Required argument `{error.param.name}` missing"
        elif isinstance(error, commands.CommandOnCooldown):
            embed.description = f"Cooldown - please retry this command in {round(error.retry_after)} second(s)"
        elif isinstance(error, commands.DisabledCommand):
            embed.description = f"Command {ctx.command} has been disabled"
        elif isinstance(error, commands.NoPrivateMessage):
            embed.description = "This command cannot be used in DMs"
            try:
                return await ctx.author.send(embed=embed)
            except discord.errors.Forbidden:
                return
        elif isinstance(error, commands.CheckFailure):
            embed.description = (
                f"Permissions check for command {ctx.command} failed - you may not have the required permissions"
            )
        elif isinstance(error, (commands.ConversionError, commands.BadArgument, commands.UserInputError)):
            embed.description = str(error)
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            return await ctx.send(
                "A wild exception appears!",
                view=Traceback(ctx, "".join(traceback.format_exception(type(error), error, error.__traceback__))),
            )
        return await ctx.send(embed=embed)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(ErrorHandler(bot))
