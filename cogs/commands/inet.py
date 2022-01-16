import sys
from io import BytesIO

import discord
from discord.ext import commands

from utils.functions import get_youtube_url


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
        _urls = urls.split()
        await ctx.send(f":movie_camera: Downloading {len(_urls)} video(s)")
        successful_downloads = 0
        for url in _urls:
            if url.startswith("ytsearch:"):
                await ctx.send(":movie_camera: ytsearch is not supported, you can only use URLs")
                continue
            dest_url = await self.bot.loop.run_in_executor(None, get_youtube_url, url)
            async with self.bot.httpsession.get(dest_url, headers=self.bot.HTTP_HEADERS) as vid:
                buf = BytesIO(await vid.read())
            if sys.getsizeof(buf) > ctx.guild.filesize_limit:
                await ctx.send(
                    f":movie_camera: Output file is larger than this server's filesize limit ({ctx.guild.filesize_limit/float(1<<20):,.0f}MB)"
                )
                continue
            else:
                await ctx.send(file=discord.File(buf, filename="download.mp4"))
                successful_downloads += 1
                del buf
        return await ctx.send(f":movie_camera: Downloaded {successful_downloads} video(s)")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Internet(bot))
