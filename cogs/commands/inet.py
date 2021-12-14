from datetime import datetime
from io import BytesIO
from urllib.parse import quote_plus

import asyncio
import discord
import sys
import wikipedia
import youtube_dl
from discord.ext import commands


class Internet(commands.Cog):
    def __init__(self, bot):
        """Internet related commands"""
        self.bot = bot
        
    async def get_youtube(self, url):
        ydl_opts = {
            "format": "best",
            "outtmpl": "mp4",
            "forceurl": True,
            "quiet": True
        }
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            return ydl.extract_info(url, download=False)["formats"][-1]["url"]
            

    @commands.command(
        name="lmgtfy",
        aliases=["google", "websearch"],
        brief="Pass a query and get your link!",
        description="Return a link to 'Let me Google that for you', a simplified Google for dummies",
    )
    async def lmgtfy(
        self,
        ctx,
        *,
        query: str = commands.Option(description="What would you like to query?"),
    ):
        """Let me Google that for you - pass a query and get your link"""
        await ctx.send(f"https://lmgtfy.app/?q={quote_plus(query)}")

    @commands.command(
        name="isgd",
        aliases=["vgd", "urlshort"],
        brief="Shorten multiple URLS",
        description="Use the is.gd API to batch shorten URLs - rate limits apply!",
    )
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def isgd(
        self,
        ctx,
        *,
        urls: str = commands.Option(description="One or more URLs to shorten"),
    ):
        """Batch-shorten up to 5 URLs at a time with the is.gd API"""
        if len(urls.split()) > 5:
            await ctx.send("No more than 5 URLs can be shortened at a time")
            return

        for url in urls.split():
            async with self.bot.httpsession.get(f"https://is.gd/create.php?format=json&url={url}", headers=self.bot.config.get("aiohttp_base_headers")) as r:
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

    @commands.command(
        name="wikipedia",
        aliases=["wiki", "encyclopedia"],
        brief="Query Wikipedia for information",
        description="Use the Wikipedia API to query a page and get info on it",
    )
    async def wikipedia(self, ctx, *, query: str = commands.Option(description="Search Wikipedia")):
        """Query Wikipedia, the free encyclopedia."""
        try:
            page = wikipedia.page(query, auto_suggest=False)
            embed = discord.Embed(
                title=page.title,
                url=page.url,
                description=wikipedia.summary(query, sentences=3, auto_suggest=False, redirect=True, chars=1000),
                color=ctx.author.color or ctx.guild.me.color,
                timestamp=datetime.utcnow(),
            )
        except wikipedia.DisambiguationError as e:

            await ctx.send("Disambiguation: choose one of the following:")
            await ctx.send("```\n" + ", ".join(e.options) + "\n```")

            try:
                msg = await self.bot.wait_for(
                    "message",
                    check=lambda msg: msg.author == ctx.author
                    and msg.channel == ctx.channel
                    and msg.content in e.options,
                )
            except ValueError:
                return await ctx.send(f":x: | Invalid choice")

            if msg.content not in e.options:
                return await ctx.send(":x: | Invalid choice")

            query = e.options[e.options.index(msg.content)]

            try:
                page = wikipedia.page(query, auto_suggest=False)
                embed = discord.Embed(
                    title=page.title,
                    url=page.url,
                    description=wikipedia.summary(query, sentences=3, auto_suggest=False, redirect=True, chars=1000),
                    color=ctx.author.color or ctx.guild.me.color,
                )
            except wikipedia.DisambiguationError as e:
                pass
            except wikipedia.PageError:
                return await ctx.send(
                    f":globe_with_meridians: | Page ID `{query}` doesn't match any pages - maybe that page doesn't exist? Try another."
                )

            return await ctx.send(embed=embed)

        except wikipedia.PageError:
            return await ctx.send(
                f":globe_with_meridians: | Page ID `{query}` doesn't match any pages - maybe that page doesn't exist? Try another."
            )

        await ctx.send(embed=embed)
        
    @commands.command(name="ytdl", aliases=["youtube", "downloadvideo"], brief="Download YouTube videos", description="Download videos from YouTube with youtube_dl")
    async def ytdl(self, ctx, url: str = commands.Option(description="Enter the URL of the video")):
        buffer = BytesIO()
        
        url = await self.get_youtube(url)
        
        async with self.bot.httpsession.get(url, headers=self.bot.config.get("aiohttp_base_headers")) as vid:
            r = await vid.read()
            buffer.write(r)
        
        buffer.seek(0)
            
        if sys.getsizeof(buffer) > 8000000:
            return await ctx.send("Output file is bigger than 8MB")
        
        await ctx.send(file=discord.File(buffer, filename="download.mp4"))


def setup(bot):
    bot.add_cog(Internet(bot))
