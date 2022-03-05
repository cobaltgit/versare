import datetime
from typing import Optional

import discord
from discord.ext import commands

from utils.objects import BaseEmbed


class AFK(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        """AFK management"""
        self.bot = bot
        self.afks = {}

    async def cache_afks(self):
        self.afks = {
            guild_id: {user_id: {"message": message, "timestamp": timestamp}}
            for user_id, guild_id, message, timestamp in await self.bot.db.fetch("SELECT * FROM afk")
        }

    @commands.command(name="afk", brief="Set your AFK", description="Set your AFK and notify other users")
    async def afk(
        self,
        ctx: commands.Context,
        *,
        message: Optional[str] = commands.Option(
            description="The message you want to display to others", default="No reason provided"
        ),
    ) -> discord.Message:
        ts = datetime.datetime.utcnow()
        embed = BaseEmbed(title="AFK Set", color=ctx.author.color)
        embed.set_footer(text=ctx.author, icon_url=ctx.author.avatar.url)
        embed.add_field(name="Reason", value=message, inline=True)
        await ctx.reply(embed=embed)
        self.afks.update({ctx.guild.id: {ctx.author.id: {"message": message, "timestamp": ts}}})
        if await self.bot.db.fetchval(
            "SELECT user_id FROM afk WHERE user_id = $1 AND guild_id = $2", ctx.author.id, ctx.guild.id
        ):
            await self.bot.db.execute(
                "UPDATE afk SET user_id = $1, message = $2 WHERE user_id = $1 AND guild_id = $3",
                ctx.author.id,
                message,
                ctx.guild.id,
            )
        else:
            await self.bot.db.execute(
                "INSERT INTO afk (user_id, guild_id, message, timestamp) VALUES($1, $2, $3, $4)",
                ctx.author.id,
                ctx.guild.id,
                message,
                ts,
            )

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message) -> bool | discord.Message:

        if message.author == self.bot.user:
            return False

        if not self.afks:
            await self.cache_afks()

        members = [m.id for m in message.guild.members if m.id in self.afks.get(message.guild.id, {})]

        for m in members:
            if message.author == message.guild.get_member(m):
                embed = BaseEmbed(title="Welcome back!", color=message.author.color)
                embed.set_footer(text=message.author, icon_url=message.author.avatar.url)
                embed.add_field(
                    name="Reason", value=self.afks[message.guild.id][message.author.id]["message"], inline=True
                )
                embed.add_field(
                    name="Duration",
                    value=discord.utils.format_dt(
                        self.afks[message.guild.id][message.author.id]["timestamp"], style="R"
                    ),
                    inline=True,
                )
                await message.channel.send(embed=embed, reference=message)
                self.afks[message.guild.id].pop(m, None)
                await self.bot.db.execute("DELETE FROM afk WHERE user_id = $1 AND guild_id = $2", m, message.guild.id)
            elif (member := message.guild.get_member(m)).mentioned_in(message):
                await message.channel.send(
                    f"{member} is AFK - '{self.afks[message.guild.id][member.id]['message']}'", reference=message
                )


def setup(bot: commands.Bot) -> None:
    bot.add_cog(AFK(bot))
