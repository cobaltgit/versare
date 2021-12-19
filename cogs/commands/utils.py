import os
import sys
from datetime import datetime

import discord
from discord.ext import commands


class Utilities(commands.Cog):
    """General utilities"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="restart", brief="Restart the bot", description="Restart the bot with exec [ OWNER ONLY ]", hidden=True
    )
    @commands.is_owner()
    async def restart(self, ctx):
        await ctx.send("Restarting bot...")
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Restarting bot")
        await self.bot.close()
        os.execv(sys.executable, ["python"] + sys.argv)

    @commands.group(name="logging", brief="Server audit logs", description="Manage audit logs for this server")
    @commands.has_permissions(manage_guild=True, manage_channels=True)
    async def logging(self, ctx):
        if not ctx.invoked_subcommand:
            async with self.bot.guild_cxn.cursor() as cur:
                await cur.execute("SELECT log_channel_id FROM logging WHERE guild_id = ?", (ctx.guild.id,))
                result = await cur.fetchone()
                if result:
                    await ctx.send(f"Log channel for this guild is {self.bot.get_channel(int(result[0]))}")
                else:
                    await ctx.send("This guild has no log channel")

    @logging.command(
        name="setchn", brief="Set the log channel", description="Set the audit log channel for this server"
    )
    async def setchn(self, ctx, channel: discord.TextChannel = commands.Option(description="Channel to log events in")):
        async with self.bot.guild_cxn.cursor() as cur:
            await cur.execute("SELECT log_channel_id FROM logging WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if not result:
                await cur.execute(
                    "INSERT INTO logging (log_channel_id, guild_id) VALUES (?, ?)",
                    (
                        channel.id,
                        ctx.guild.id,
                    ),
                )
            else:
                await cur.execute(
                    "UPDATE logging SET log_channel_id = ? WHERE guild_id = ?", (channel.id, ctx.guild.id)
                )
            await self.bot.guild_cxn.commit()
            await cur.close()
        return await ctx.send(f"Log channel for this guild is now {channel}")


def setup(bot):
    bot.add_cog(Utilities(bot))
