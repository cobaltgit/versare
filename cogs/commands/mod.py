from datetime import datetime
from typing import Optional

import discord
from discord.ext import commands


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
            await self.bot.db_cur.execute("SELECT * FROM sniper WHERE channel_id = ?", (ctx.message.channel.id,))
            result = await self.bot.db_cur.fetchone()
            if not result:
                await ctx.send(":envelope: | No message to snipe")
                return
            author = ctx.message.guild.get_member(result[1])
            channel = ctx.message.guild.get_channel(result[0])
            embed = discord.Embed(
                description=self.bot.fernet.decrypt(result[2]).decode("utf-8"),
                color=author.color,
                timestamp=datetime.utcnow(),
            )
            embed.set_author(name=author, icon_url=author.avatar.url)
            embed.set_footer(text=f"Message sniped from #{channel}")
            await ctx.send(embed=embed)

    @snipe.command(name="optout", brief="Opt out of being sniped or editsniped")
    async def optout(self, ctx):
        """Opt out of being sniped or editsniped"""
        await self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
        result = await self.bot.db_cur.fetchone()
        if result is None:
            await self.bot.db_cur.execute(
                "INSERT INTO sniper_optout(user_id, guild_id) VALUES (?, ?)", (ctx.author.id, ctx.guild.id)
            )
            await self.bot.db_cxn.commit()
            await ctx.send(":envelope: | You have successfully opted out of being sniped.")
            return

        if ctx.author.id in result:
            await ctx.send(":envelope: | You are already opted out of being sniped.")

    @snipe.command(
        name="optin",
        brief="Opt in to being sniped or editsniped",
        description="Opt back in to being sniped or edit-sniped by others",
    )
    async def optin(self, ctx):
        """Opt back in to being sniped"""
        await self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (ctx.guild.id,))
        result = await self.bot.db_cur.fetchone()

        if result and ctx.author.id in result:
            await self.bot.db_cur.execute(
                "DELETE FROM sniper_optout WHERE user_id = ? AND guild_id = ?",
                (
                    ctx.author.id,
                    ctx.guild.id,
                ),
            )
            await self.bot.db_cxn.commit()
            await ctx.send(":envelope: | You have successfully opted back in being sniped.")
            return

        if not result or ctx.author.id not in result:
            await ctx.send(":envelope: | You are already opted in to being sniped.")

    @commands.command(
        name="editsnipe",
        aliases=["esnipe"],
        brief="Get the contents of the last edited message before and after",
        description="Get the contents of the last edited message before and after - some users may opt out, so if they edit a message and you try to snipe it, nothing is returned.",
    )
    async def editsnipe(self, ctx):
        await self.bot.db_cur.execute("SELECT * FROM editsniper WHERE channel_id = ?", (ctx.message.channel.id,))
        result = await self.bot.db_cur.fetchone()
        if not result:
            await ctx.send(":envelope: | No message to editsnipe")
            return
        author = ctx.message.guild.get_member(result[1])
        channel = ctx.message.guild.get_channel(result[0])
        embed = discord.Embed(
            color=author.color,
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
        members: commands.Greedy[discord.Member],
        delete_message_days: Optional[int] = commands.Option(
            description="How many days of messages from the member should be deleted?", default=0
        ),
        *,
        reason: Optional[str] = commands.Option(
            description="Why are you banning these members?", default="No reason specified"
        ),
    ):
        for member in members:
            if member.top_role.position > ctx.guild.me.top_role.position or member.guild_permissions.administrator:
                await ctx.send(f"You do not have permission to ban `{member}`")
            else:
                try:
                    await member.send(f"You have been banned from {ctx.guild}.\nReason: {reason}")
                except (discord.errors.Forbidden, discord.errors.HTTPException):
                    await ctx.send(f"I could not DM member `{member}`")
                await member.ban(delete_message_days=delete_message_days, reason=reason)
                await ctx.send(f"Banned member `{member}`.\nReason: {reason}")

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
        for member in members:
            if member.top_role.position > ctx.guild.me.top_role.position or member.guild_permissions.administrator:
                await ctx.send(f"You do not have permission to kick `{member}`")
            else:
                try:
                    await member.send(f"You have been kicked from {ctx.guild}\nReason: {reason}")
                except (discord.errors.Forbidden, discord.errors.HTTPException):
                    await ctx.send(f"I could not DM member `{member}`")
                await member.kick(reason=reason)
                await ctx.send(f"Kicked member `{member}`\nReason: {reason}")


def setup(bot):
    bot.add_cog(Moderation(bot))
