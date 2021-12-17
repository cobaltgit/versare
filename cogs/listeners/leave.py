import discord
from discord.ext import commands


class LeaveListener(commands.Cog):
    """Listen for guild leave events"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_guild_leave(self, guild):
        try:
            self.bot.prefixes.pop(str(guild.id))
        except KeyError:
            pass
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("DELETE FROM custompfx WHERE guild_id = ?", (guild.id,))
            await cur.close()
        await self.bot.guild_cxn.commit()


def setup(bot):
    bot.add_cog(LeaveListener(bot))
