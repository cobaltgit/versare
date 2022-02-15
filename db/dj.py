import discord
from discord.ext import commands


async def set_dj(ctx: commands.Context, role: discord.Role) -> None:
    if await ctx.bot.db.execute("SELECT role_id FROM dj WHERE guild_id = $1", ctx.guild.id):
        await ctx.bot.db.execute("UPDATE dj SET role_id = $1 WHERE guild_id = $2", role.id, ctx.guild.id)
    else:
        await ctx.bot.db.execute("INSERT INTO dj (role_id, guild_id) VALUES ($1, $2)", role.id, ctx.guild.id)


async def get_dj(ctx: commands.Context) -> None | discord.Role:
    return (
        None
        if not (role_id := await ctx.bot.db.fetchval("SELECT role_id FROM dj WHERE guild_id = $1", ctx.guild.id))
        else ctx.guild.get_role(role_id)
    )


async def check_dj_perms(ctx: commands.Context, member: discord.Member) -> bool:
    return (dj_role := await get_dj(ctx)) in member.roles or member.guild_permissions.manage_guild
