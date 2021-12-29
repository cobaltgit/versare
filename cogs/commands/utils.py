import sys
from datetime import timedelta
from inspect import getsource
from io import BytesIO
from platform import python_version
from time import time
from typing import Optional

import discord
import psutil
from discord.ext import commands
from pkg_resources import get_distribution

from utils.objects import BaseEmbed


class Utilities(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot
        self.proc = psutil.Process()
        self.GITHUB_URL = "https://github.com/cobaltgit/versare"
        self.GIT_BRANCH = "rewrite"
        self.HELP_COMMAND_FILE = "./utils/help.py"

    @commands.command(
        name="ping",
        brief="Get latency information",
        description="Get the websocket, API and PostgreSQL database latency values",
    )
    async def ping(self, ctx):
        api_start = time()
        msg = await ctx.send("Ping...")
        api_end = time()

        postgres_start = time()
        await self.bot.db.fetch("SELECT 1;")
        postgres_end = time()

        embed = BaseEmbed(title="Pong!", color=ctx.author.color)
        fields = [
            (":globe_with_meridians: Websocket", f"{round(self.bot.latency * 1000)}ms", False),
            (":desktop: REST API", f"{round((api_end - api_start) * 1000)}ms", False),
            (
                "<:PostgreSQL:923564294526885918> Database",
                f"{round((postgres_end - postgres_start) * 1000)}ms",
                False,
            ),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await msg.edit(content=None, embed=embed)

    @commands.command(
        name="about",
        aliases=["version", "info"],
        brief="Get information about the bot",
        description="Get version information of the bot, Python, discord.py and PostgreSQL server",
    )
    async def about(self, ctx):
        pg_ver = await self.bot.db.fetchval("SHOW server_version")
        api_start = time()
        msg = await ctx.send("Getting ping...")
        api_end = time()
        pg_start = time()
        await self.bot.db.fetchval("SELECT 1;")
        pg_end = time()
        bot_owner = await self.bot.fetch_user(self.bot.config["auth"].get("owner_id")) or "Not specified"
        embed = BaseEmbed(
            title="About Me",
            description="Information about the bot (version, latency, etc) is all listed below",
            color=ctx.guild.me.color,
        )
        fields = [
            ("\u200b", "**Versions of software used**", False),
            (
                f"{self.bot.config['emojis']['versare']} Versare"
                if self.bot.config.get("emojis", {}).get("versare")
                else "Versare",
                self.bot.__version__,
                True,
            ),
            (
                f"{self.bot.config['emojis']['python']} Python"
                if self.bot.config.get("emojis", {}).get("python")
                else "Python",
                python_version(),
                True,
            ),
            (
                f"{self.bot.config['emojis']['discord.py']} discord.py"
                if self.bot.config.get("emojis", {}).get("discord.py")
                else "discord.py",
                get_distribution("discord.py").version,
                True,
            ),
            (
                f"{self.bot.config['emojis']['postgres']} PostgreSQL Server"
                if self.bot.config.get("emojis", {}).get("postgres")
                else "PostgreSQL Server",
                pg_ver.split()[0],
                True,
            ),
            ("\u200b", "**Latency to the REST API, websocket and database**", False),
            (":globe_with_meridians: WS Latency", f"{round(self.bot.latency * 1000)}ms", True),
            (":desktop: REST Latency", f"{round((api_end - api_start) * 1000)}ms", True),
            (
                f"{self.bot.config['emojis']['postgres']} DB Latency"
                if self.bot.config.get("emojis", {}).get("postgres")
                else "DB Latency",
                f"{round((pg_end - pg_start) * 1000)}ms",
                True,
            ),
            ("\u200b", "**Uptime, process and other info**", False),
            (
                ":computer: Process Usage",
                f"RAM: {self.proc.memory_full_info().uss / 1024**2:.2f}MB\nCPU: {self.proc.cpu_percent() / psutil.cpu_count():.2f}%",
                True,
            ),
            (":stopwatch: Uptime", str(timedelta(seconds=int(round(time() - self.bot.start_time)))), True),
            ("\u200b", "\u200b", True),
            (
                ":busts_in_silhouette: Guild Count",
                len([guild for guild in self.bot.guilds if not guild.unavailable]),
                True,
            ),
            (":robot: Bot Owner", bot_owner, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await msg.edit(content=None, embed=embed)

    @commands.command(
        name="source",
        aliases=["code", "command", "src", "git", "github"],
        brief="Get source code of a command or the bot",
        description="Fetch and send the source code of a bot command if specified or the GitHub repository",
    )
    async def source(
        self, ctx, *, command: Optional[str] = commands.Option(description="Specify a command:", default=None)
    ):
        if not command:
            return await ctx.send(f"Link to source code on GitHub\n{self.GITHUB_URL}/tree/{self.GIT_BRANCH}")
        elif command == "help":
            return await ctx.send(file=discord.File(self.HELP_COMMAND_FILE, filename="help.py"))
        cmd = self.bot.get_command(command)
        fn = cmd.callback
        src = getsource(fn)

        buf = BytesIO()
        buf.write(src.encode('utf-8'))
        buf.seek(0)
        
        await ctx.send(file=discord.File(buf, filename=command.replace(" ", "_") + ".py"))


def setup(bot):
    bot.add_cog(Utilities(bot))
