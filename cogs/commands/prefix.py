from discord.ext import commands


class Prefix(commands.Cog):
    """Prefix management commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", invoke_without_command=True)
    async def prefix(self, ctx):
        prefix = (
            await self.bot.db.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", ctx.guild.id)
            or self.bot.config["defaults"]["prefix"]
        )
        await ctx.send("Prefix for this guild is `%s`" % prefix)

    @prefix.command(name="set")
    async def set(self, ctx, prefix: str = commands.Option(description="Prefix for this guild (max 8 characters)")):
        if len(prefix) > 8:
            return ctx.send("Must be no more than 8 characters")

        await self.bot.db.execute("UPDATE prefixes SET prefix = $1 WHERE guild_id = $2", prefix, ctx.guild.id)
        self.bot.prefixes[str(ctx.guild.id)] = prefix
        await ctx.send("Prefix for this guild is now `%s`" % prefix)


def setup(bot):
    bot.add_cog(Prefix(bot))
