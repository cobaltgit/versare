import os
import sys
from datetime import datetime

from discord.ext import commands


class Utilities(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="restart", brief="Restart the bot", description="Restart the bot with exec [ OWNER ONLY ]")
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Restarting bot...")
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Restarting bot")
        await self.bot.close()
        os.execv(sys.executable, ["python"] + sys.argv)


def setup(bot):
    bot.add_cog(Utilities(bot))
