from datetime import datetime, timedelta
from time import time

import discord
from discord.ext import commands


class Stats(commands.Cog):
    """Bot statistics"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        self.start_time = time()

    @commands.command(name="ping", brief="Get the latency between you and the bot")
    async def ping(self, ctx):
        """Get the latency between you and the bot"""
        api_start = time()
        msg = await ctx.send("Ping...")
        api_end = time()
        embed = discord.Embed(title="Pong!", color=ctx.author.color, timestamp=datetime.utcnow())
        fields = [
            ("Websocket Latency", str(round(self.bot.latency * 1000)) + "ms", True),
            ("API Latency", str(round((api_end - api_start) * 1000)) + "ms", True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/ping-pong_1f3d3.png"
        )
        await msg.edit(content=f"{ctx.author.mention}", embed=embed)

    @commands.command(name="uptime", brief="Get how long the bot has been running")
    async def uptime(self, ctx):
        """Get how long the bot has been running"""
        embed = discord.Embed(
            title="Uptime",
            description=f"The bot has been up {timedelta(seconds=int(round(time()-self.start_time)))}",
            color=ctx.author.color,
        )
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/stopwatch_23f1-fe0f.png"
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="serverinfo",
        brief="Get information about the server",
        description="Collect stats for the server (members, roles, categories, channels, etc.)",
    )
    async def serverinfo(self, ctx):
        """Display information about the server (members, roles, categories, channels, etc.)"""
        embed = discord.Embed(title=f"Server Info for {ctx.guild}", color=ctx.guild.roles[-1].color)
        fields = [
            ("Guild ID", ctx.guild.id, True),
            ("Guild Owner", ctx.guild.owner, True),
            ("\u200B", "\u200B", True),
            ("Members", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
            ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
            ("\u200B", "\u200B", True),
            ("Roles", len(ctx.guild.roles), True),
            ("Categories", len(ctx.guild.categories), True),
            ("\u200B", "\u200B", True),
            ("Text Channels", len(ctx.guild.text_channels), True),
            ("Voice Channels", len(ctx.guild.voice_channels), True),
        ]
        if ctx.guild.features:
            fields.append(("\u200B", "\u200B", True))
            fields.append(("Features", "✅" + "\n✅".join(ctx.guild.features), True))
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if ctx.guild.banner:
            embed.set_image(url=ctx.guild.banner.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
