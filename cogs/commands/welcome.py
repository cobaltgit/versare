import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="welcome",
        brief="Welcome commands",
        description="Welcome commands - if no subcommand is passed, return the welcome message and channel for the guild",
    )
    async def welcome(self, ctx):
        """Get the welcome message and channel for this guild"""
        if ctx.invoked_subcommand is not None:
            return

        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                welcome_message = self.bot.config["defaults"]["welcome_msg"]
            else:
                welcome_message = str(result[0])

            await cur.execute("SELECT welcome_channel_id FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                if ctx.guild.system_channel is None:
                    welcome_channel = None
                else:
                    welcome_channel = ctx.guild.system_channel.id
            else:
                welcome_channel = result[0]

        await ctx.send(
            f"""**WELCOME**
The welcome channel for this guild is `{self.bot.get_channel(welcome_channel)}`
The welcome message for this guild is '{welcome_message}'"""
        )

    @welcome.command(
        name="setchn",
        brief="Set the channel for welcome messages",
        description="Set the channel for welcome messages to be sent in",
    )
    @commands.has_permissions(manage_guild=True, manage_channels=True, manage_messages=True)
    async def setchn(
        self,
        ctx,
        channel: discord.TextChannel = commands.Option(description="Specify the channel you would like to use"),
    ):
        """Set the welcome message channel for this guild"""
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT welcome_channel_id FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                sql = "INSERT INTO welcome (guild_id,welcome_channel_id) VALUES (?,?)"
                val = (ctx.guild.id, channel.id)
            else:
                sql = "UPDATE welcome SET welcome_channel_id = ? WHERE guild_id = ?"
                val = (channel.id, ctx.guild.id)
            await cur.execute(sql, val)
            await self.bot.guild_cxn.commit()
            await cur.close()
        await ctx.send(f"Welcome channel is now `{channel}`")

    @welcome.command(
        name="setmsg",
        brief="Set the welcome message to send when a new member joins",
        description="Set the welcome message to automatically send when a new member joins the server",
    )
    @commands.has_permissions(manage_guild=True, manage_channels=True, manage_messages=True)
    async def setmsg(
        self,
        ctx,
        *,
        msg: str = commands.Option(
            description="Set the welcome message for this guild - {0} denotes the guild name, {1} denotes the member name"
        ),
    ):
        """Set the welcome message for this guild - {0} denotes the guild name, {1} denotes the member name"""
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                sql = "INSERT INTO welcome (guild_id,welcome_message) VALUES (?,?)"
                val = (ctx.guild.id, msg)
            else:
                sql = "UPDATE welcome SET welcome_message = ? WHERE guild_id = ?"
                val = (msg, ctx.guild.id)
            await cur.execute(sql, val)
            await self.bot.guild_cxn.commit()
            await cur.close()
        await ctx.send(f"Welcome message for this guild is now '{msg}'")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute(
                "SELECT welcome_channel_id FROM welcome WHERE guild_id = ?",
                (member.guild.id,),
            )
            result = await cur.fetchone()
            if result is None:
                if member.guild.system_channel is None:
                    return
                welcome_channel = member.guild.system_channel
            else:
                welcome_channel = self.bot.get_channel(result[0])

            await cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (member.guild.id,))
            result = await self.bot.guild_cur.fetchone()
            await cur.close()
        welcome_message = str(result[0]) if result else self.bot.config["defaults"]["welcome_msg"]

        await welcome_channel.send(welcome_message.format(member.guild, member.mention))

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        if guild.system_channel is None:
            if "general" in guild.channels:
                welcome_channel = discord.utils.get(guild.channels, name="general").id
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(
                            "System channel not found for this guild. Falling back to `#general` for welcome channel."
                        )
                    break
            else:
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        await channel.send(
                            f"Welcome channel not set! Enter command `{self.bot.config['defaults']['prefix']}welcome setchn <channel>` to set it."
                        )
                    break
                return
        else:
            welcome_channel = guild.system_channel
        async with self.bot.guild_cxn.cursor() as cur:
            await self.bot.guild_cur.execute("SELECT * FROM welcome WHERE guild_id = ?", (guild.id,))
            result = await self.bot.guild_cur.fetchone()
            if not result:
                await self.bot.guild_cur.execute(
                    "INSERT INTO welcome(welcome_message, welcome_channel_id, guild_id)",
                    (
                        self.bot.config["welcome_msg"],
                        welcome_channel.id,
                        guild.id,
                    ),
                )
            else:
                await self.bot.guild_cur.execute(
                    "UPDATE welcome SET welcome_message = ? WHERE guild_id = ?",
                    (self.bot.config["welcome_msg"], guild.id),
                )
                await self.bot.guild_cur.execute(
                    "UPDATE welcome SET welcome_channel_id = ? WHERE guild_id = ?",
                    (welcome_channel, guild.id),
                )
            await self.bot.guild_cxn.commit()
            await cur.close()


def setup(bot):
    bot.add_cog(Welcome(bot))
