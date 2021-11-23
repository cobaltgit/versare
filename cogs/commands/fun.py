from datetime import datetime
from random import choice, randint
from typing import Optional

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """Other fun commands"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="pp")
    async def pp(
        self,
        ctx,
        person: Optional[discord.Member] = commands.Option(
            description="Who's PP size do you want to measure?", default=None
        ),
    ):
        person = person or ctx.author
        size = "8" + "".join(["=" for _ in range(randint(0, 20))]) + "D"
        embed = discord.Embed(
            title="PP Size",
            description=f"{person.mention}'s PP Size\n{size} ({len(size)}cm)",
            color=person.color or 0x0047AB,
            timestamp=datetime.utcnow(),
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
