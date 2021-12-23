from datetime import datetime
from time import time

import discord
from discord.ext import commands


class Utilities(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot

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

        embed = discord.Embed(title="Pong!", color=ctx.author.color, timestamp=datetime.utcnow())
        fields = [
            (":globe_with_meridians: Websocket", "%dms" % round(self.bot.latency * 1000), False),
            (":desktop: REST API", "%dms" % round((api_end - api_start) * 1000), False),
            (
                "<:PostgreSQL:923564294526885918> Database",
                "%dms" % round((postgres_end - postgres_start) * 1000),
                False,
            ),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await msg.edit(content=None, embed=embed)


def setup(bot):
    bot.add_cog(Utilities(bot))
