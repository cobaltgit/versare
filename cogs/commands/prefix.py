from __future__ import annotations

import discord
from discord.ext import commands

import db.prefix


class Prefix(commands.Cog):
    """Prefix management commands"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(
        name="prefix",
        brief="Get the prefix for this server",
        description="Fetch server prefix from database cache",
        invoke_without_command=True,
    )
    async def prefix(self, ctx: commands.Context) -> discord.Message:

        return await ctx.send(
            f"Prefix for this guild is `{self.bot.prefixes.get(ctx.guild.id, self.bot.config['defaults']['prefix'])}`"
        )

    @prefix.command(
        name="set", brief="Set the prefix for this server", description="Add server prefix to the database and cache"
    )
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def set(
        self,
        ctx: commands.Context,
        prefix: str = commands.Option(description="Prefix for this guild (max 8 characters)"),
    ) -> discord.Message:

        await db.prefix.upsert_prefix(ctx, prefix)
        return await ctx.send(f"Prefix for this guild is now `{prefix}`")

    @commands.Cog.listener()
    async def on_guild_leave(self, guild: discord.Guild) -> None:
        self.bot.prefixes.pop(guild.id, None)
        await self.bot.db.execute("DELETE FROM prefix WHERE guild_id = $1", guild.id)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Prefix(bot))
