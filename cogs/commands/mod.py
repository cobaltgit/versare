from __future__ import annotations
from discord.ext import commands
import discord
from utils.objects import BaseEmbed


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
        target = await self.bot.db.fetchrow("SELECT * FROM sniper WHERE channel_id = $1", ctx.message.channel.id)
        if not target:
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
        user_optout = await self.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", ctx.guild.id)

        if user_optout and ctx.author.id in user_optout:
            return await ctx.send(":envelope: You have already opted out of being sniped")

        await self.bot.db.execute(
            "INSERT INTO snipe_optout(user_id, guild_id) VALUES ($1, $2)", ctx.author.id, ctx.guild.id
        )
        return await ctx.send(":envelope: You have sucessfully opted out of being sniped")

    @snipe.command(
        name="optin",
        brief="Opt back in to being sniped",
        description="Opt back in to having your deleted messages sniped by other users",
    )
    async def optin(self, ctx: commands.Context) -> discord.Message:
        user_optout = await self.bot.db.fetchrow("SELECT * FROM snipe_optout WHERE guild_id = $1", ctx.guild.id)
        if ctx.author.id not in user_optout:
            return await ctx.send(":envelope: You are already opted in to being sniped")

        await self.bot.db.execute(
            "DELETE FROM snipe_optout WHERE user_id = $1 AND guild_id = $2", ctx.author.id, ctx.guild.id
        )
        return await ctx.send(":envelope: You have successfully opted in to being sniped")

    @snipe.command(
        name="edit",
        aliases=["e"],
        brief="Get the previous contents of the last edited message",
        description="Get the previous contents of the last edited message in the channel - some users may opt out, which the sniper will ignore",
    )
    async def editsnipe(self, ctx: commands.Context) -> discord.Message:
        target = await self.bot.db.fetchrow("SELECT * FROM editsniper WHERE channel_id = $1", ctx.message.channel.id)
        if not target:
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


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Moderation(bot))
