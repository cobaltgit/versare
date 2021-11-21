from datetime import datetime

import discord
from discord.ext import commands


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(name="snipe")
    async def snipe(self, ctx):
        """Get the last deleted message from a channel"""
        if ctx.invoked_subcommand is None:
            self.bot.db_cur.execute("SELECT * FROM sniper WHERE channel_id = ?", (ctx.message.channel.id,))
            result = self.bot.db_cur.fetchone()
            if not result:
                await ctx.send(":envelope: | No message to snipe")
                return
            author = ctx.message.guild.get_member(result[1])
            channel = ctx.message.guild.get_channel(result[0])
            embed = discord.Embed(
                description=self.bot.fernet.decrypt(result[2]).decode("utf-8"),
                color=author.color,
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=author, icon_url=author.avatar.url)
            embed.set_footer(text=f"Message sniped from #{channel}")
            await ctx.send(embed=embed)

    @snipe.command(name="optout")
    async def optout(self, ctx):
        """Opt out of being sniped"""
        self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()
        if result is None:
            self.bot.db_cur.execute(
                "INSERT INTO sniper_optout(user_id, guild_id) VALUES (?, ?)", (ctx.author.id, ctx.guild.id)
            )
            self.bot.db_cxn.commit()
            await ctx.send(":envelope: | You have successfully opted out of being sniped.")
            return

        if ctx.author.id in result:
            await ctx.send(":envelope: | You are already opted out of being sniped.")

    @snipe.command(name="optin")
    async def optin(self, ctx):
        """Opt back in to being sniped"""
        self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
        result = self.bot.db_cur.fetchone()

        if result and ctx.author.id in result:
            self.bot.db_cur.execute(
                "DELETE FROM sniper_optout WHERE user_id = ? AND guild_id = ?",
                (
                    ctx.author.id,
                    ctx.guild.id,
                ),
            )
            self.bot.db_cxn.commit()
            await ctx.send(":envelope: | You have successfully opted back in being sniped.")
            return

        if not result or ctx.author.id not in result:
            await ctx.send(":envelope: | You are already opted in to being sniped.")


def setup(bot):
    bot.add_cog(Moderation(bot))
