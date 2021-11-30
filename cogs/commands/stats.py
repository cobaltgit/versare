import re
from datetime import datetime, timedelta
from platform import python_version
from subprocess import check_output
from time import time
from typing import Optional

import discord
import psutil
from discord.ext import commands
from pkg_resources import get_distribution


class Stats(commands.Cog):
    """Bot statistics"""

    def __init__(self, bot):
        self.bot = bot
        self.proc = psutil.Process()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.start_time = time()

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
        embed = discord.Embed(
            title=f"Server Info for {ctx.guild}", color=ctx.guild.roles[-1].color, timestamp=datetime.utcnow()
        )
        fields = [
            ("Guild ID", ctx.guild.id, True),
            ("Guild Owner", ctx.guild.owner, True),
            ("\u200B", "\u200B", True),
            ("Server Creation Date", ctx.guild.created_at.strftime("%b %d, %Y at %H:%M:%S"), True),
            ("\u200B", "\u200B", True),
            ("Members", len(list(filter(lambda m: not m.bot, ctx.guild.members))), True),
            ("Bots", len(list(filter(lambda m: m.bot, ctx.guild.members))), True),
            ("\u200B", "\u200B", True),
            ("Roles", len(ctx.guild.roles), True),
            ("Categories", len(ctx.guild.categories), True),
            ("\u200B", "\u200B", True),
            ("Text Channels", len(ctx.guild.text_channels), True),
            ("Voice Channels", len(ctx.guild.voice_channels), True),
            ("\u200B", "\u200B", True),
            ("Boosts", ctx.guild.premium_subscription_count, True),
            ("Boost Level", ctx.guild.premium_tier, True),
        ]
        if ctx.guild.premium_subscriber_role:
            fields.append(
                (
                    "Boosters",
                    "\n".join((str(A) for A in ctx.guild.premium_subscriber_role.members)),
                    False,
                )
            )
        else:
            fields.append(("\u200B", "\u200B", True))
        if ctx.guild.features:
            fields.extend(
                (
                    ("\u200B", "\u200B", True),
                    (
                        "Features",
                        "✅" + "\n✅".join(str(feature).replace("_", " ").title() for feature in ctx.guild.features),
                        False,
                    ),
                )
            )
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if ctx.guild.banner:
            embed.set_image(url=ctx.guild.banner.url)
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.command(
        name="whois",
        aliases=["userinfo", "profile"],
        brief="Get information on a user in the server",
        description="Get information about a user (roles, permissions, etc.)",
    )
    async def whois(
        self,
        ctx,
        user: Optional[discord.Member] = commands.Option(
            description="Who would you like to get info about?", default=None
        ),
    ):
        user = user or ctx.author
        embed = discord.Embed(description=user.mention, color=ctx.author.color, timestamp=datetime.utcnow())
        fields = [
            ("Server Join Date", user.joined_at.strftime("%b %d, %Y at %H:%M:%S"), True),
            ("Account Register Date", user.created_at.strftime("%b %d, %Y at %H:%M:%S"), True),
            ("\u200B", "\u200B", True),
            ("Bot", user.bot, True),
            ("Nickname", user.nick, True) if user.nick else ("\u200B", "\u200B", True),
            ("\u200B", "\u200B", True),
            (
                f"Roles [{len(user.roles) - 1}]",
                " ".join(str(role.mention) for role in user.roles[1:]),
                False if (len(user.roles) - 1) else ("\u200B", "\u200B", True),
            ),
            (
                "Moderation Permissions",
                ", ".join(
                    str(perm).replace("_", " ").title()
                    for perm, value in user.guild_permissions
                    if re.search("^m(anage|ute)|deafen|kick|ban|mention|view|administrator", perm.lower())
                ),
                False,
            ),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name=user, icon_url=user.avatar.url)
        embed.set_thumbnail(url=user.avatar.url)
        embed.set_footer(text=f"User ID: {user.id}")
        await ctx.send(embed=embed)

    @commands.command(
        name="about",
        aliases=["version", "aboutme"],
        brief="Get the version of the bot",
        description="Get the version of the bot, Python and discord.py",
    )
    async def about(self, ctx):
        """Get the version of the bot and"""
        embed = discord.Embed(title="About Me", color=0x0047AB, timestamp=datetime.utcnow())
        fields = [
            (
                "<:Versare:914949604078927912> Versare",
                f"`git-{check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('utf-8')}`",
                True,
            ),
            ("<:Python:914950534887243776> Python", f"`{python_version()}`", True),
            ("<:Discordpy:914951096974323793> Discord.py", f"`{get_distribution('discord.py').version}`", True),
            (
                ":computer: Process Usage",
                f"RAM: {self.proc.memory_full_info().uss / 1024**2:.2f}MB\nCPU: {self.proc.cpu_percent() / psutil.cpu_count():.2f}%",
                False,
            ),
            (":stopwatch: Uptime", str(timedelta(seconds=int(round(time() - self.bot.start_time)))), True),
            (
                ":busts_in_silhouette: Guild Count",
                len([guild for guild in self.bot.guilds if not guild.unavailable]),
                True,
            ),
            (":robot: Bot Owner", await self.bot.fetch_user(self.bot.config["owner_id"]), True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=self.bot.user.avatar.url)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Stats(bot))
