from datetime import datetime

import discord
from discord.ext import commands

from lib.functions import get_log_channel


class Logging(commands.Cog):
    """Logging event listeners"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_ban(self, guild, member):
        log_channel = await get_log_channel(guild)
        log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.ban).flatten()
        log = log[0]

        embed = discord.Embed(title="User Banned", color=log.user.color, timestamp=datetime.utcnow())
        fields = [
            ("User", log.target, True),
            ("ID", log.target.id, True),
            ("\u200B", "\u200B", True),
            ("Moderator", log.user, True),
            ("Reason", log.reason, True),
        ]
        embed.set_thumbnail(url=log.target.avatar.url)
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if log_channel:
            await self.bot.get_channel(log_channel).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_unban(self, guild, member):
        log_channel = await get_log_channel(guild)
        log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.unban).flatten()
        log = log[0]

        embed = discord.Embed(title="User Unbanned", color=log.user.color, timestamp=datetime.utcnow())
        fields = [
            ("User", log.target, True),
            ("ID", log.target.id, True),
        ]
        embed.set_thumbnail(url=log.target.avatar.url)
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if log_channel:
            await self.bot.get_channel(log_channel).send(embed=embed)

    @commands.Cog.listener()
    async def on_member_kick(self, guild, member):
        log_channel = await get_log_channel(guild)
        log = await guild.audit_logs(limit=1, action=discord.AuditLogAction.kick).flatten()
        log = log[0]

        embed = discord.Embed(title="User Kicked", color=log.user.color, timestamp=datetime.utcnow())
        fields = [
            ("User", log.target, True),
            ("ID", log.target.id, True),
            ("\u200B", "\u200B", True),
            ("Moderator", log.user, True),
            ("Reason", log.reason, True),
        ]
        embed.set_thumbnail(url=log.target.avatar.url)
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        if log_channel:
            await self.bot.get_channel(log_channel).send(embed=embed)


def setup(bot):
    bot.add_cog(Logging(bot))
