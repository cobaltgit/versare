from datetime import timedelta
from platform import python_version
from time import time

import psutil
from discord.ext import commands
from pkg_resources import get_distribution

from utils.objects import BaseEmbed


class Utilities(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot
        self.proc = psutil.Process()

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
            ("\u200b", "\u200b", True),
            (":globe_with_meridians: WS Latency", f"{round(self.bot.latency * 1000)}ms", True),
            (":desktop: REST Latency", f"{round((api_end - api_start) * 1000)}ms", True),
            (
                f"{self.bot.config['emojis']['postgres']} DB Latency"
                if self.bot.config.get("emojis", {}).get("postgres")
                else "DB Latency",
                f"{round((pg_end - pg_start) * 1000)}ms",
                True,
            ),
            ("\u200b", "\u200b", True),
            (
                ":computer: Process Usage",
                f"RAM: {self.proc.memory_full_info().uss / 1024**2:.2f}MB\nCPU: {self.proc.cpu_percent() / psutil.cpu_count():.2f}%",
                True,
            ),
            ("Uptime", str(timedelta(seconds=int(round(time() - self.bot.start_time)))), True),
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


def setup(bot):
    bot.add_cog(Utilities(bot))
