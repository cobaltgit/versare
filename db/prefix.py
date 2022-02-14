from discord.ext import commands


async def upsert_prefix(ctx: commands.Context, prefix: str) -> None:
    """Insert a custom guild prefix into the database and cache

    Args:
        ctx (commands.Context): The context to use for the bot
        prefix (str): The prefix to insert

    Raises:
        commands.BadArgument: Prefix is more than 8 characters
    """

    if len(prefix) > 8:
        raise commands.BadArgument("Prefix must be no more than 8 characters")

    if await ctx.bot.db.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", ctx.guild.id):
        await ctx.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
    else:
        await ctx.bot.db.execute("INSERT INTO prefixes (prefix, guild_id) VALUES($1, $2)", prefix, ctx.guild.id)

    ctx.bot.prefixes[str(ctx.guild.id)] = prefix
