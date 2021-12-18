from datetime import datetime
from random import choice, randint
from typing import Optional

import discord
from discord.ext import commands


class Fun(commands.Cog):
    """Other fun commands"""

    def __init__(self, bot):
        self.bot = bot

    async def get_meme(self, subreddit):
        async with self.bot.httpsession.get(
            f"https://meme-api.herokuapp.com/gimme/{subreddit}", headers=self.bot.config.get("aiohttp_base_headers")
        ) as r:
            return await r.json()

    @commands.command(
        name="pp",
        brief="Measure someone's PP size (obviously jokingly)",
        description="Measure someone's PP size (obviously jokingly)",
    )
    async def pp(
        self,
        ctx,
        person: Optional[discord.Member] = commands.Option(
            description="Who's PP size do you want to measure?", default=None
        ),
    ):
        person = person or ctx.author
        size = "8" + ("=" * randint(1, 20)) + "D"
        embed = discord.Embed(
            title="PP Size",
            description=f"{person.mention}'s PP Size\n{size} ({len(size)}cm)",
            color=person.color,
            timestamp=datetime.utcnow(),
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="meme",
        brief="Fetch a random meme from Reddit",
        description="Fetch a random meme using D3vd's Meme API from a subreddit of your choice or a random subreddit",
    )
    async def meme(
        self, ctx, subreddit: Optional[str] = commands.Option(description="Choose a subreddit (OPTIONAL)", default=None)
    ):
        """Fetch a random meme from a subreddit of your choice or a random one with D3vd's Meme API"""
        meme_subs = self.bot.config["memes"]["default_subreddits"]
        resp = await self.get_meme(subreddit or choice(meme_subs))

        retries = 0
        retry_limit = self.bot.config["memes"]["retry_limit"] or 5
        while (resp["nsfw"] or resp["spoiler"]) and (retries < retry_limit):
            retries += 1
            resp = await self.get_meme(subreddit or choice(meme_subs))
            if not resp["nsfw"] and not resp["spoiler"]:
                break
        if retries == retry_limit:
            return await ctx.send(f":underage: | {retry_limit} failed attempts to find an SFW meme. Please try again.")

        embed = discord.Embed(
            title=resp["title"],
            url=resp["postLink"],
            color=ctx.author.color or ctx.guild.me.color,
            timestamp=datetime.utcnow(),
        )

        embed.set_image(url=resp["url"])

        fields = [
            ("Author", f"u/{resp['author']}", True),
            ("Subreddit", f"r/{resp['subreddit']}", True),
            ("Upvotes", resp["ups"], True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)

        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Fun(bot))
