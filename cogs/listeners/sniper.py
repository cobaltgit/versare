from __future__ import annotations

import asyncio
import contextlib

import discord
from discord.ext import commands


class Sniper(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message) -> None:
        user_optout = await self.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", message.guild.id)
        if user_optout and message.author.id in list(user_optout):
            return

        await self.bot.db.execute("DELETE FROM sniper WHERE channel_id = $1", message.channel.id)
        self.encrypted_message = self.bot.fernet.encrypt(message.content.encode("utf-8"))

        await self.bot.db.execute(
            "INSERT INTO sniper(user_id, channel_id, message) VALUES ($1, $2, $3)",
            message.author.id,
            message.channel.id,
            self.encrypted_message,
        )
        await asyncio.sleep(30)
        await self.bot.db.execute("DELETE FROM sniper WHERE channel_id = $1", message.channel.id)
        with contextlib.suppress(AttributeError, NameError):
            del self.encrypted_message

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message) -> None:
        user_optout = await self.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", before.guild.id)
        if user_optout and before.author.id in list(user_optout):
            return

        await self.bot.db.execute("DELETE FROM editsniper WHERE channel_id = $1", before.channel.id)
        self.encrypted_before = self.bot.fernet.encrypt(before.content.encode("utf-8"))
        self.encrypted_after = self.bot.fernet.encrypt(after.content.encode("utf-8"))

        await self.bot.db.execute(
            "INSERT INTO editsniper(before, after, user_id, channel_id) VALUES ($1, $2, $3, $4)",
            self.encrypted_before,
            self.encrypted_after,
            before.author.id,
            before.channel.id,
        )
        await asyncio.sleep(30)
        await self.bot.db.execute("DELETE FROM editsniper WHERE channel_id = $1", before.channel.id)
        with contextlib.suppress(AttributeError, NameError):
            del self.encrypted_before
            del self.encrypted_after


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Sniper(bot))
