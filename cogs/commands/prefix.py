from discord.ext import commands


class Prefix(commands.Cog):
    """Manage custom prefixes"""

    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="prefix", brief="Get the prefix for the guild you are in")
    async def prefix(self, ctx):
        """Get the prefix for this server"""
        if ctx.invoked_subcommand is None:
            prefix = self.bot.prefixes.get(str(ctx.guild.id)) or self.bot.config["defaults"]["prefix"]
            await ctx.send(f"Prefix for this guild is `{prefix}`")

    @prefix.command(name="set", brief="Set the prefix for the guild you are in")
    @commands.has_permissions(manage_guild=True)
    async def set(
        self,
        ctx,
        prefix: str = commands.Option(description="Specify the prefix you want to use"),
    ):
        """Set custom prefix for server"""
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                await cur.execute(
                    "INSERT INTO custompfx(prefix, guild_id) VALUES(?,?)",
                    (
                        prefix,
                        ctx.guild.id,
                    ),
                )
            else:
                await cur.execute(
                    "UPDATE custompfx SET prefix = ? WHERE guild_id = ?",
                    (
                        prefix,
                        ctx.guild.id,
                    ),
                )
            await self.bot.guild_cxn.commit()
            await cur.close()
        self.bot.prefixes[str(ctx.guild.id)] = prefix
        await ctx.send(f"Prefix for this guild is now `{prefix}`")

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT * FROM custompfx WHERE guild_id = ?", (guild.id,))
            result = await cur.fetchone()
            if not result:
                await cur.execute(
                    "INSERT INTO custompfx(prefix, guild_id) VALUES (?,?)",
                    (
                        self.bot.config["defaults"]["prefix"],
                        guild.id,
                    ),
                )
            else:
                await cur.execute(
                    "UPDATE custompfx SET prefix = ? WHERE guild_id = ?",
                    (self.bot.config["defaults"]["prefix"], guild.id),
                )
            await self.bot.guild_cxn.commit()
            await cur.close()
        self.bot.prefixes[str(guild.id)] = self.bot.config["defaults"]["prefix"]

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.content == f"<@!{self.bot.user.id}>":
            async with self.bot.guild_cxn.cursor() as cur:
                await cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (message.guild.id,))
                result = await cur.fetchone()
                await cur.close()
            prefix = self.bot.config["defaults"]["prefix"] if result is None else str(result[0])
            await message.channel.send(f"Prefix for this guild is `{prefix}`")


def setup(bot):
    bot.add_cog(Prefix(bot))
