from discord.ext import commands


class Prefix(commands.Cog):
    """Prefix management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        await ctx.send("Prefix for this guild is `%s`" % self.bot.prefixes[str(ctx.guild.id)])

    @prefix.command(name="set")
    @commands.check_any(commands.has_permissions(manage_guild=True), commands.is_owner())
    async def set(self, ctx, prefix: str = commands.Option(description="Prefix for this guild (max 8 characters)")):
        if len(prefix) > 8:
            return ctx.send("Must be no more than 8 characters")

        await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
        self.bot.prefixes[str(ctx.guild.id)] = prefix
        await ctx.send("Prefix for this guild is now `%s`" % prefix)


def setup(bot):
    bot.add_cog(Prefix(bot))
