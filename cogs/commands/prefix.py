from discord.ext import commands


class Prefix(commands.Cog):
    """Prefix management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="prefix",
        brief="Get the prefix for this server",
        description="Fetch server prefix from database cache",
        invoke_without_command=True,
    )
    async def prefix(self, ctx):
        await ctx.send("Prefix for this guild is `%s`" % self.bot.prefixes[str(ctx.guild.id)])

    @prefix.command(
        name="set", brief="Set the prefix for this server", description="Add server prefix to the database and cache"
    )
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def set(self, ctx, prefix: str = commands.Option(description="Prefix for this guild (max 8 characters)")):
        if len(prefix) > 8:
            return ctx.send("Must be no more than 8 characters")

        prefix_exists = await self.bot.db.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", ctx.guild.id)
        if not prefix_exists:
            await self.bot.db.execute("INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)", ctx.guild.id, prefix)
        else:
            await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
        self.bot.prefixes[str(ctx.guild.id)] = prefix
        await ctx.send("Prefix for this guild is now `%s`" % prefix)


def setup(bot):
    bot.add_cog(Prefix(bot))
