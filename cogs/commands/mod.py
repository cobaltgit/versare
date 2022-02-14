from __future__ import annotations

from contextlib import suppress
from typing import Optional

import discord
from discord.ext import commands

import db.snipe
from utils.objects import BaseEmbed, TimeConverter


class Moderation(commands.Cog):
    """Moderation commands (kick, ban, snipe deleted messages, etc)"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.group(
        name="snipe",
        brief="Get the last deleted message from a channel",
        description="Get the last deleted message from a channel - some users may opt out, for which the sniper will ignore.",
        invoke_without_command=True,
    )
    async def snipe(self, ctx: commands.Context) -> discord.Message:
        await ctx.defer()
        if not (target := await db.snipe.get_snipe(ctx)):
            return await ctx.send(":envelope: No message to snipe")

        author = ctx.guild.get_member(target[1])
        channel = ctx.guild.get_channel(target[2])

        embed = BaseEmbed(
            description=self.bot.fernet.decrypt(target[0]).decode("utf-8"),
            color=author.color or ctx.author.color or ctx.guild.me.color,
        )
        embed.set_author(name=author, icon_url=author.avatar.url)
        embed.set_footer(text=f"Message sniped from #{channel}")

        return await ctx.send(embed=embed)

    @snipe.command(
        name="optout",
        brief="Opt out of being sniped",
        description="Opt out of having your deleted messages sniped by other users",
    )
    async def optout(self, ctx: commands.Context) -> discord.Message:
        await ctx.defer()
        if await db.snipe.optout(ctx):
            return await ctx.send(":envelope: You have sucessfully opted out of being sniped")
        else:
            return await ctx.send(":envelope: You have already opted out of being sniped")

    @snipe.command(
        name="optin",
        brief="Opt back in to being sniped",
        description="Opt back in to having your deleted messages sniped by other users",
    )
    async def optin(self, ctx: commands.Context) -> discord.Message:
        await ctx.defer()
        if await db.snipe.optin(ctx):
            return await ctx.send(":envelope: You have successfully opted in to being sniped")
        else:
            return await ctx.send(":envelope: You are already opted in to being sniped")

    @snipe.command(
        name="edit",
        aliases=["e"],
        brief="Get the previous contents of the last edited message",
        description="Get the previous contents of the last edited message in the channel - some users may opt out, which the sniper will ignore",
    )
    async def editsnipe(self, ctx: commands.Context) -> discord.Message:
        await ctx.defer()
        if not (target := await db.snipe.get_editsnipe(ctx)):
            return await ctx.send(":envelope: No message to editsnipe")

        author = ctx.guild.get_member(target[2])
        channel = ctx.guild.get_channel(target[3])

        embed = BaseEmbed(color=author.color or ctx.author.color or ctx.guild.me.color)
        fields = [
            ("Before", self.bot.fernet.decrypt(target[0]).decode("utf-8"), True),
            ("After", self.bot.fernet.decrypt(target[1]).decode("utf-8"), True),
        ]
        embed.set_author(name=author, icon_url=author.avatar.url)
        embed.set_footer(text=f"Message sniped from #{channel}")
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        return await ctx.send(embed=embed)

    @commands.command(
        name="timeout",
        aliases=["mute", "stfu", "silence"],
        brief="Time out members from the server",
        description="Time out members from the server for any duration between 1 second and 28 days",
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx: commands.Context,
        member: discord.Member = commands.Option(description="Who to time out?"),
        duration: Optional[str] = commands.Option(description="How long will the mute last?", default="10m"),
        *,
        reason: Optional[str] = commands.Option(description="Why are you muting them?", default="No reason provided"),
    ) -> discord.Message:
        await ctx.defer()
        try:
            _duration = TimeConverter(duration)
        except ValueError:
            return await ctx.send(":stopwatch: Invalid duration")
        if not 1 <= _duration.seconds <= 2419200:
            return await ctx.send(f":stopwatch: Duration must be between 1 second and 28 days, got {_duration}")
        if member.timed_out:
            return await ctx.send(
                f":stopwatch: Member {member} is already timed out for {TimeConverter(member.timeout_until.timestamp()-ctx.message.created_at.timestamp())}"
            )
        try:
            await member.edit(timeout_until=discord.utils.utcnow() + _duration.delta)
        except discord.errors.Forbidden:
            return await ctx.send(f":stopwatch: You do not have permission to mute {member}")
        with suppress(discord.errors.Forbidden):
            await member.send(f"You have been muted in {ctx.guild} for {_duration}\nReason: {reason}")
        return await ctx.send(f":stopwatch: Timed out member {member.mention} for {_duration}")

    @commands.command(
        name="slowmode",
        aliases=["slow", "snail"],
        brief="Enable slowmode for a channel",
        description="Set the slowmode duration for a channel",
    )
    async def slowmode(
        self,
        ctx: commands.Context,
        channel: Optional[discord.TextChannel] = commands.Option(
            description="Channel to apply slowmode to (defaults to current channel", default=None
        ),
        duration: Optional[str] = commands.Option(description="Duration of the slowmode", default="5s"),
    ) -> discord.Message:
        await ctx.defer()
        channel = channel or ctx.channel
        try:
            duration_conv = TimeConverter(duration)
        except ValueError:
            return await ctx.send(":slowmode: Invalid duration")
        if not 1 <= duration_conv.seconds <= 21600:
            return await ctx.send(
                f":snail: Duration out of range: {duration_conv} - must be between 1 second and 6 hours"
            )
        if channel.slowmode_delay == duration_conv.seconds:
            return await ctx.send(
                f":snail: Slowmode is already enabled for channel {channel.mention} for {TimeConverter(channel.slowmode_delay)}"
            )
        await channel.edit(slowmode_delay=duration_conv.seconds)
        return await ctx.send(f":snail: Applied slowmode to channel {channel.mention} for {duration_conv}")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
