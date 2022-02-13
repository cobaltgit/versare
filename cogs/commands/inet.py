import sys
import traceback
from io import BytesIO
from urllib.parse import urlparse

import discord
from discord.ext import commands
from youtube_dl import YoutubeDL

from utils.views import Traceback


class Internet(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.command(
        name="ytdl",
        aliases=["download", "youtube"],
        brief="Download videos using youtube-dl",
        description="Batch download videos from a variety of sites using youtube-dl to your server.",
    )
    async def ytdl(
        self, ctx: commands.Context, *, urls: str = commands.Option(description="Enter one or more URLs to download")
    ) -> discord.Message:
        await ctx.defer()
        _urls = [url for url in urls.split() if all((urlparse(url).scheme, urlparse(url).netloc))]
        if not any(_urls):
            return await ctx.send(":movie_camera: Please provide one or more valid URLs to download")
        await ctx.send(f":movie_camera: Downloading {len(_urls)} video(s)")
        successful_downloads = 0
        for url in _urls:
            try:
                dest_url = await self.bot.loop.run_in_executor(
                    None, lambda: YoutubeDL({"quiet": True}).extract_info(url, download=False)["formats"][-1]["url"]
                )
            except Exception as e:
                await ctx.send(
                    f":movie_camera: Failed to download video #{_urls.index(url) + 1} as youtube-dl caught an exception",
                    view=Traceback(ctx, "".join(traceback.format_exception(type(e), e, e.__traceback__))),
                )
                continue
            async with self.bot.httpsession.get(dest_url, headers=self.bot.HTTP_HEADERS) as vid:
                buf = BytesIO(await vid.read())
            if sys.getsizeof(buf) > ctx.guild.filesize_limit:
                await ctx.send(
                    f":movie_camera: Output file for video #{_urls.index(url) + 1} is larger than this server's filesize limit ({ctx.guild.filesize_limit/float(1<<20):,.0f}MB)"
                )
                continue
            else:
                await ctx.send(file=discord.File(buf, filename="download.mp4"))
                successful_downloads += 1
                del buf
        return await ctx.send(f":movie_camera: Downloaded {successful_downloads} video(s)")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Internet(bot))
