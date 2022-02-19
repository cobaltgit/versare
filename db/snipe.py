import asyncio
import contextlib

import discord
from discord.ext import commands


async def snipe_message(ctx: commands.Context, message: discord.Message) -> None:
    user_optout = await ctx.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", message.guild.id)
    if user_optout and message.author.id in list(user_optout):
        return

    await ctx.bot.db.execute("DELETE FROM sniper WHERE channel_id = $1", message.channel.id)
    encrypted_message = ctx.bot.fernet.encrypt(message.content.encode("utf-8"))

    await ctx.bot.db.execute(
        "INSERT INTO sniper(user_id, channel_id, message) VALUES ($1, $2, $3)",
        message.author.id,
        message.channel.id,
        encrypted_message,
    )
    await asyncio.sleep(30)
    await ctx.bot.db.execute("DELETE FROM sniper WHERE channel_id = $1", message.channel.id)
    with contextlib.suppress(NameError):
        del encrypted_message


async def snipe_edit(ctx: commands.Context, before: discord.Message, after: discord.Message):
    user_optout = await ctx.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", before.guild.id)
    if user_optout and before.author.id in list(user_optout):
        return

    await ctx.bot.db.execute("DELETE FROM editsniper WHERE channel_id = $1", before.channel.id)
    encrypted_before = ctx.bot.fernet.encrypt(before.content.encode("utf-8"))
    encrypted_after = ctx.bot.fernet.encrypt(after.content.encode("utf-8"))

    await ctx.bot.db.execute(
        "INSERT INTO editsniper(before, after, user_id, channel_id) VALUES ($1, $2, $3, $4)",
        encrypted_before,
        encrypted_after,
        before.author.id,
        before.channel.id,
    )
    await asyncio.sleep(30)
    await ctx.bot.db.execute("DELETE FROM editsniper WHERE channel_id = $1", before.channel.id)
    with contextlib.suppress(NameError):
        del encrypted_before
        del encrypted_after


async def get_snipe(ctx: commands.Context):
    return await ctx.bot.db.fetchrow("SELECT * FROM sniper WHERE channel_id = $1", ctx.message.channel.id)


async def get_editsnipe(ctx: commands.Context):
    return await ctx.bot.db.fetchrow("SELECT * FROM editsniper WHERE channel_id = $1", ctx.message.channel.id)


async def optout(ctx: commands.Context):
    snipe_optout = await ctx.bot.db.fetchval(
        "SELECT * FROM snipe_optout WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id
    )
    if snipe_optout:
        return False
    else:
        return await ctx.bot.db.execute(
            "INSERT INTO snipe_optout(user_id, guild_id) VALUES ($1, $2)", ctx.author.id, ctx.guild.id
        )


async def optin(ctx: commands.Context):
    snipe_optout = await ctx.bot.db.fetchval(
        "SELECT * FROM snipe_optout WHERE guild_id = $1 AND user_id = $2", ctx.guild.id, ctx.author.id
    )
    if not snipe_optout:
        return False
    else:
        return await ctx.bot.db.execute(
            "DELETE FROM snipe_optout WHERE user_id = $1 AND guild_id = $2", ctx.author.id, ctx.guild.id
        )
