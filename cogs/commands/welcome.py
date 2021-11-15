import discord
from discord.ext import commands


class Welcome(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_check(self, ctx):
        return ctx.author.guild_permissions.administrator

    @commands.group(name="welcome")
    async def welcome(self, ctx):
        if ctx.invoked_subcommand is not None:
            return

        self.bot.db_cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            welcome_message = self.bot.config["defaults"]["welcome_msg"]
        else:
            welcome_message = str(result[0])

        self.bot.db_cur.execute("SELECT welcome_channel_id FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
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

    @welcome.command(name="setchn")
    async def setchn(
        self,
        ctx,
        channel: discord.TextChannel = commands.Option(description="Specify the channel you would like to use"),
    ):
        """Set the welcome message channel for this guild"""
        self.bot.db_cur.execute("SELECT welcome_channel_id FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            sql = "INSERT INTO welcome (guild_id,welcome_channel_id) VALUES (?,?)"
            val = (ctx.guild.id, channel.id)
        else:
            sql = "UPDATE welcome SET welcome_channel_id = ? WHERE guild_id = ?"
            val = (channel.id, ctx.guild.id)
        self.bot.db_cur.execute(sql, val)
        self.bot.db_cxn.commit()
        await ctx.send(f"Welcome channel is now `{channel}`")

    @welcome.command(name="setmsg")
    async def setmsg(
        self,
        ctx,
        *,
        msg: str = commands.Option(
            description="Set the welcome message for this guild - {0} denotes the guild name, {1} denotes the member name"
        ),
    ):
        """Set the welcome message for this guild - {0} denotes the guild name, {1} denotes the member name"""
        self.bot.db_cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            sql = "INSERT INTO welcome (guild_id,welcome_message) VALUES (?,?)"
            val = (ctx.guild.id, msg)
        else:
            sql = "UPDATE welcome SET welcome_message = ? WHERE guild_id = ?"
            val = (msg, ctx.guild.id)
        self.bot.db_cur.execute(sql, val)
        self.bot.db_cxn.commit()
        await ctx.send(f"Welcome message for this guild is now '{msg}'")

    @commands.Cog.listener()
    async def on_member_join(self, member: discord.Member):
        self.bot.db_cur.execute("SELECT welcome_channel_id FROM welcome WHERE guild_id = ?", (member.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            if member.guild.system_channel is None:
                return
            welcome_channel = member.guild.system_channel
        else:
            welcome_channel = self.bot.get_channel(result[0])

        self.bot.db_cur.execute("SELECT welcome_message FROM welcome WHERE guild_id = ?", (member.guild.id,))
        result = self.bot.db_cur.fetchone()
        welcome_message = str(result[0]) if result is not None else self.bot.config["defaults"]["welcome_msg"]

        await welcome_channel.send(welcome_message.format(member.guild, member.mention))


def setup(bot):
    bot.add_cog(Welcome(bot))
