from discord.ext import commands


class Prefix(commands.Cog):
    """Manage custom prefixes"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix")
    async def prefix(self, ctx):
        """Get the prefix for this server"""
        if ctx.invoked_subcommand is None:
            self.bot.db_cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (ctx.guild.id,))
            result = self.bot.db_cur.fetchone()
            prefix = self.bot.config["defaults"]["prefix"] if result is None else str(result[0])
            await ctx.send(f"Prefix for this guild is `{prefix}`")

    @prefix.command(name="set")
    @commands.has_permissions(manage_guild=True)
    async def set(
        self,
        ctx,
        prefix: str = commands.Option(description="Specify the prefix you want to use"),
    ):
        """Set custom prefix for server"""
        self.bot.db_cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            self.bot.db_cur.execute(
                "INSERT INTO custompfx(prefix, guild_id) VALUES(?,?)",
                (
                    prefix,
                    ctx.guild.id,
                ),
            )
        else:
            self.bot.db_cur.execute(
                "UPDATE custompfx SET prefix = ? WHERE guild_id = ?",
                (
                    prefix,
                    ctx.guild.id,
                ),
            )
        self.bot.db_cxn.commit()
        await ctx.send(f"Prefix for this guild is now `{prefix}`")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        self.bot.db_cur.execute("SELECT * FROM custompfx WHERE guild_id = ?", (guild.id,))
        result = self.bot.db_cur.fetchone()
        if not result:
            self.bot.db_cur.execute(
                "INSERT INTO custompfx(prefix, guild_id)",
                (
                    self.bot.config["default_prefix"],
                    guild.id,
                ),
            )
        else:
            self.bot.db_cur.execute(
                "UPDATE custompfx SET prefix = ? WHERE guild_id = ?",
                (self.bot.config["default_prefix"], guild.id),
            )
        self.bot.db_cxn.commit()

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == f"<@!{self.bot.user.id}>":
            self.bot.db_cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (message.guild.id,))
            result = self.bot.db_cur.fetchone()
            prefix = self.bot.config["default_prefix"] if result is None else str(result[0])
            await message.channel.send(f"Prefix for this guild is `{prefix}`")


def setup(bot):
    bot.add_cog(Prefix(bot))
