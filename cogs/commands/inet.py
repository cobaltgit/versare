from urllib.parse import quote_plus

from discord.ext import commands


class Internet(commands.Cog):
    def __init__(self, bot):
        """Internet related commands"""
        self.bot = bot

    @commands.command(name="lmgtfy", aliases=["google", "websearch"])
    async def lmgtfy(self, ctx, *, query: str = commands.Option(description="What would you like to query?")):
        await ctx.send(f"https://lmgtfy.app/?q={quote_plus(query)}")

    @commands.command(name="isgd", aliases=["vgd", "urlshort"])
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def isgd(self, ctx, *, urls: str = commands.Option(description="One or more URLs to shorten")):
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


def setup(bot):
    bot.add_cog(Internet(bot))
