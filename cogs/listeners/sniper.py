from __future__ import annotations

import discord
from discord.ext import commands

import db.snipe


class Sniper(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        ctx = await self.bot.get_context(message)
        await db.snipe.snipe_message(ctx, message)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        ctx = await self.bot.get_context(before)
        await db.snipe.snipe_edit(ctx, before, after)


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Sniper(bot))
