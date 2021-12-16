from typing import Optional

import discord
import datetime
from discord.ext import commands


class Tags(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="tag",
        brief="Call a server tag",
        description="Call a tag in the server or create one",
        invoke_without_command=True,
    )
    async def tag(
        self,
        ctx,
        *,
        calltag: Optional[str] = commands.Option(description="What tag would you like to call?", default=None),
    ):
        """Call a server tag or use the group commands"""

        if calltag is None:
            return

        if calltag not in [cmd.name for cmd in self.tag.commands]:
            async with self.bot.tags_cxn.cursor() as cur:
                await self.bot.tags_cur.execute("SELECT * FROM tags WHERE guild_id = ?", (ctx.guild.id,))
                result = await self.bot.tags_cur.fetchall()
                await cur.close()
            if not result:
                return await ctx.send("There are no tags here.")

            try:
                wanted_tag = [list(row) for row in result if calltag in row][0][1]
            except IndexError:
                await ctx.send(f"`{calltag}`: no such tag")
            else:
                await ctx.send(wanted_tag)

    @tag.command(name="make", brief="Interactively make a tag")
    async def make(self, ctx):
        """Interactively create a tag"""

        check = lambda msg: (msg.author, msg.channel) == (ctx.author, ctx.channel)

        await ctx.send("Enter the name of the tag")

        tname = await self.bot.wait_for("message", check=check)

        await ctx.send("Enter the contents of the tag")

        contents = await self.bot.wait_for("message", check=check)

        async with self.bot.tags_cxn.cursor() as cur:
            await cur.execute(
                "INSERT INTO tags(guild_id, owner_id, tag, content, creation_dt) VALUES (?, ?, ?, ?, ?)",
                (
                    ctx.guild.id,
                    ctx.author.id,
                    str(tname),
                    str(contents),
                    datetime.datetime.utcnow().timestamp()
                ),
            )
            await self.bot.tags_cxn.commit()
            await cur.close()

        await ctx.send(f"Tag `{tname}` successfully created")

    @tag.command(
        name="remove",
        aliases=["delete", "rm"],
        brief="Remove a tag",
        description="Remove a tag from the guild in the database",
    )
    async def rm(
        self, ctx, *, tag: str = commands.Option(description="Enter the name of the tag you would like to remove")
    ):
        """Remove a tag from the database"""
        async with self.bot.tags_cxn.cursor() as cur:
            await self.bot.tags_cur.execute(
                "SELECT tag FROM tags WHERE tag = ? AND guild_id = ?",
                (
                    tag,
                    ctx.guild.id,
                ),
            )
            result = await self.bot.tags_cur.fetchone()
            
        if not result:
            return await ctx.send(f"`{tag}`: no such tag")
            
        async with self.bot.tags_cxn.cursor() as cur:
            await cur.execute(
                "DELETE FROM tags WHERE tag = ? AND guild_id = ?",
                (
                    tag,
                    ctx.guild.id,
                ),
            )
            await self.bot.tags_cxn.commit()
            await cur.close()

        await ctx.send(f"Tag `{tag}` successfully removed")
        
    @tag.command(name="owner", brief="Get the owner of a tag", description="Get the owner of a tag from the database")
    async def owner(self, ctx, *, tag: str = commands.Option(description="Enter the name of the tag")):
        await self.bot.tags_cur.execute("SELECT owner_id, creation_dt, content FROM tags WHERE tag = ? AND guild_id = ?", (tag,ctx.guild.id,))
        result = await self.bot.tags_cur.fetchone()
        author = ctx.guild.get_member(result[0])
        if not result:
            return await ctx.send(f"`{tag}`: no such tag")
        embed = discord.Embed(title=tag, timestamp=datetime.datetime.fromtimestamp(result[1]), color=author.color)
        embed.set_author(name=author, icon_url=author.avatar.url)
        embed.set_footer(text="Date of tag creation")
        fields = [
            ("Owner", author.mention, True),
            ("Tag Contents", result[2], True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Tags(bot))
