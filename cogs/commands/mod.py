from datetime import datetime, timedelta
from typing import Literal, Optional, Union

import discord
from discord.ext import commands

from lib.functions import get_log_channel


class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="snipe",
        brief="Get the last deleted message from a channel",
        description="Get the last deleted message from a channel - some users may opt out, so if they've deleted a message and you try to snipe it, nothing is returned",
    )
    async def snipe(self, ctx):
        """Get the last deleted message from a channel"""
        if ctx.invoked_subcommand is None:
            async with self.bot.snipe_cxn.cursor() as cur:
                await cur.execute("SELECT * FROM sniper WHERE channel_id = ?", (ctx.message.channel.id,))
                result = await cur.fetchone()
                await cur.close()

            if not result:
                return await ctx.send(":envelope: | No message to snipe")

            author = ctx.message.guild.get_member(result[1])
            channel = ctx.message.guild.get_channel(result[0])

            embed = discord.Embed(
                description=self.bot.fernet.decrypt(result[2]).decode("utf-8"),
                color=author.color or ctx.guild.me.color,
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=author, icon_url=author.avatar.url)
            embed.set_footer(text=f"Message sniped from #{channel}")
            await ctx.send(embed=embed)

    @snipe.command(name="optout", brief="Opt out of being sniped or editsniped")
    async def optout(self, ctx):
        """Opt out of being sniped or editsniped"""
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result is None:
                await cur.execute(
                    "INSERT INTO sniper_optout(user_id, guild_id) VALUES (?, ?)", (ctx.author.id, ctx.guild.id)
                )
                await self.bot.snipe_cxn.commit()
                await cur.close()
                return await ctx.send(":envelope: | You have successfully opted out of being sniped.")

            if ctx.author.id in result:
                return await ctx.send(":envelope: | You are already opted out of being sniped.")

    @snipe.command(
        name="optin",
        brief="Opt in to being sniped or editsniped",
        description="Opt back in to being sniped or edit-sniped by others",
    )
    async def optin(self, ctx):
        """Opt back in to being sniped"""
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()

            if result and ctx.author.id in result:
                await cur.execute(
                    "DELETE FROM sniper_optout WHERE user_id = ? AND guild_id = ?",
                    (
                        ctx.author.id,
                        ctx.guild.id,
                    ),
                )
                await self.bot.snipe_cxn.commit()
                await cur.close()
                return await ctx.send(":envelope: | You have successfully opted back in being sniped.")

            return await ctx.send(":envelope: | You are already opted in to being sniped.")

    @commands.command(
        name="editsnipe",
        aliases=["esnipe"],
        brief="Get the contents of the last edited message before and after",
        description="Get the contents of the last edited message before and after - some users may opt out, so if they edit a message and you try to snipe it, nothing is returned.",
    )
    async def editsnipe(self, ctx):
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("SELECT * FROM editsniper WHERE channel_id = ?", (ctx.message.channel.id,))
            result = await cur.fetchone()
            await cur.close()

        if not result:
            return await ctx.send(":envelope: | No message to editsnipe")

        author = ctx.message.guild.get_member(result[1])
        channel = ctx.message.guild.get_channel(result[0])
        embed = discord.Embed(
            color=author.color or ctx.guild.me.color,
            timestamp=datetime.utcnow(),
        )
        fields = [
            ("Before", self.bot.fernet.decrypt(result[2]).decode("utf-8"), True),
            ("After", self.bot.fernet.decrypt(result[3]).decode("utf-8"), True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_author(name=author, icon_url=author.avatar.url)
        embed.set_footer(text=f"Message sniped from #{channel}")
        await ctx.send(embed=embed)

    @commands.command(
        name="ban", brief="Ban members from the server", description="Ban one or more users from the server"
    )
    @commands.has_permissions(ban_members=True)
    async def ban(
        self,
        ctx,
        members: commands.Greedy[Union[discord.Member, discord.User]],
        delete_message_days: Optional[int] = commands.Option(
            description="How many days of messages from the members should be deleted?", default=0
        ),
        *,
        reason: Optional[str] = commands.Option(
            description="Why are you banning these members?", default="No reason specified"
        ),
    ):
        """Ban members from the server"""

        await get_log_channel(ctx.guild)

        for user in members:
            if isinstance(user, discord.Member):
                if user.top_role.position > ctx.author.top_role.position:
                    await ctx.send(f":hammer: You do not have permission to ban {user}")
                else:
                    try:
                        await user.send(f"You have been banned from {ctx.guild}.\nReason: {reason}")
                    except (discord.errors.Forbidden, discord.errors.HTTPException):
                        await ctx.send(f"I could not DM user `{user}`")
                    await user.ban(delete_message_days=delete_message_days, reason=reason)
            else:
                user = await self.bot.fetch_user(int(user))
                await ctx.guild.ban(user, reason=reason)

            return await ctx.send(f":hammer: Banned {user}")

    @commands.command(
        name="kick", brief="Kick members from the server", description="Kick one or more users from the server"
    )
    @commands.has_permissions(kick_members=True)
    async def kick(
        self,
        ctx,
        members: commands.Greedy[discord.Member],
        *,
        reason: Optional[str] = commands.Option(
            description="Why are you kicking these members?", default="No reason specified"
        ),
    ):
        """Kick members from the server"""
        for member in members:
            if member.top_role.position > ctx.guild.me.top_role.position:
                await ctx.send(f"You do not have permission to kick {member}")
            else:
                try:
                    await member.send(f"You have been kicked from {ctx.guild}\nReason: {reason}")
                except (discord.errors.Forbidden, discord.errors.HTTPException):
                    await ctx.send(f"I could not DM member `{member}`")
                await member.kick(reason=reason)
                return await ctx.send(f":boot: Kicked {member}")

    @commands.command(
        name="purge",
        aliases=["clear", "clean", "prune"],
        brief="Purge up to 300 messages at a time",
        description="Purge messages from a channel, up to 300 at a time",
    )
    async def purge(
        self, ctx, amount: Optional[int] = commands.Option(description="How many messages to purge?", default=1)
    ):
        amount = min(amount, 300)
        try:
            await ctx.channel.purge(limit=amount)
        except discord.errors.Forbidden:
            return await ctx.send("You do not have permission to purge messages")
        await ctx.send(f"Purged {amount} messages", delete_after=5)

    @commands.command(
        name="timeout",
        aliases=["mute", "silence", "to"],
        brief="Mute members",
        description="Mute one or more members from chatting in the server",
    )
    @commands.has_permissions(moderate_members=True)
    async def timeout(
        self,
        ctx,
        members: commands.Greedy[discord.Member],
        duration: Optional[
            Literal[
                "30s",
                "1m",
                "5m",
                "10m",
                "30m",
                "1h",
                "2h",
                "6h",
                "12h",
                "24h",
                "2d",
                "3d",
                "1w",
                "2w",
                "3w",
                "4w",
                "Unmute",
            ]
        ] = commands.Option(description="How long for?", default="5m"),
        *,
        reason: Optional[str] = commands.Option(
            description="Why are you muting these members?", default="No reason specified"
        ),
    ):
        seconds = {
            "30s": 30,
            "1m": 60,
            "5m": 300,
            "10m": 600,
            "30m": 1800,
            "1h": 3600,
            "2h": 7200,
            "6h": 21600,
            "12h": 43200,
            "24h": 86400,
            "2d": 172800,
            "3d": 259200,
            "1w": 604800,
            "2w": 1210000,
            "3w": 1814400,
            "4w": 2419200,
        }
        for member in members:
            if duration == "Unmute":
                if not member.timeout_until:
                    return await ctx.send(f":alarm_clock: {member} is not muted")
                await member.edit(timeout_until=None, reason=reason)
                return await ctx.send(f":alarm_clock: Unmuted {member}")
            timeout_until = discord.utils.utcnow() + timedelta(seconds=seconds[duration])
            await member.edit(timeout_until=timeout_until, reason=reason)
            await ctx.send(f":shushing_face: Muted {member} for {duration}")
            try:
                await member.send(f"You have been muted from {ctx.guild} for {duration}\nReason: {reason}")
            except discord.errors.Forbidden:
                await ctx.send(f"I could not DM {member}")


def setup(bot):
    bot.add_cog(Moderation(bot))
