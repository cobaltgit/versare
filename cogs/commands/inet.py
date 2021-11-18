from urllib.parse import quote_plus

import discord
import wikipedia
from discord.ext import commands


class Internet(commands.Cog):
    def __init__(self, bot):
        """Internet related commands"""
        self.bot = bot

    @commands.command(name="lmgtfy", aliases=["google", "websearch"])
    async def lmgtfy(
        self,
        ctx,
        *,
        query: str = commands.Option(description="What would you like to query?"),
    ):
        await ctx.send(f"https://lmgtfy.app/?q={quote_plus(query)}")

    @commands.command(name="isgd", aliases=["vgd", "urlshort"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def isgd(
        self,
        ctx,
        *,
        urls: str = commands.Option(description="One or more URLs to shorten"),
    ):
        if len(urls.split()) > 5:
            await ctx.send("No more than 5 URLs can be shortened at a time")
            return

        for url in urls.split():
            async with self.bot.httpsession.get(f"https://is.gd/create.php?format=json&url={url}") as r:
                resp = await r.json(content_type="text/javascript")
            if resp.get("errorcode", False):
                if resp["errorcode"] == 1:
                    await ctx.send("Please specify a valid URL to shorten")
                elif resp["errorcode"] == 2:
                    await ctx.send("There was a problem with the URL you provided.")
                elif resp["errorcode"] == 3:
                    await ctx.send("You have reached the rate limit for the is.gd API. Please try again later.")
                elif resp["errorcode"] == 4:
                    await ctx.send(
                        "Unknown error. There may be a problem with the is.gd service or maintainence is being done on the servers. Please try again later."
                    )
                return
            await ctx.send(resp["shorturl"])

    @commands.command(name="wikipedia", aliases=["wiki", "encyclopedia"])
    async def wikipedia(self, ctx, *, query: str = commands.Option(description="Search Wikipedia")):
        """Query Wikipedia, the free encyclopedia."""
        try:
            embed = discord.Embed(
                title=wikipedia.page(query).title,
                url=wikipedia.page(query).url,
                description=wikipedia.summary(query, sentences=3, auto_suggest=True, redirect=True, chars=1000),
                color=ctx.author.color,
            )
        except wikipedia.DisambiguationError as e:

            def check(msg):
                return (
                    msg.author == ctx.author
                    and msg.channel == ctx.channel
                    and int(msg.content) in list(range(len(e.options)))
                )

            await ctx.send(f"Disambiguation: choose one of the following (0-{len(e.options)}):")
            await ctx.send("```" + "\n".join(e.options) + "```")

            msg = await self.bot.wait_for("message", check=check)

            if int(msg.content) > len(e.options):
                await ctx.send(":x: | Invalid choice")
                return

            query = e.options[int(msg.content)]

            try:
                embed = discord.Embed(
                    title=wikipedia.page(query).title,
                    url=wikipedia.page(query).url,
                    description=wikipedia.summary(query, sentences=3, auto_suggest=True, redirect=True, chars=1000),
                    color=0x0047AB,
                )
            except wikipedia.DisambiguationError as e:
                pass

            await ctx.send(embed=embed)

            return
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Internet(bot))
