from typing import Optional

import discord
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
            await self.bot.db_cur.execute("SELECT * FROM tags WHERE guild_id = ?", (ctx.guild.id,))
            result = await self.bot.db_cur.fetchall()
            if not result:
                await ctx.send("There are no tags here.")
                return

            try:
                wanted_tag = [list(row) for row in result if calltag in row][0][1]
            except IndexError:
                await ctx.send(f"`{calltag}`: no such tag")
            else:
                await ctx.send(wanted_tag)

    @tag.command(name="make", brief="Interactively make a tag")
    async def make(self, ctx):
        """Interactively create a tag"""
        await ctx.send("Enter the name of the tag")

        def check(msg):
            return (msg.author, msg.channel) == (ctx.author, ctx.channel)

        tname = await self.bot.wait_for("message", check=check)

        await ctx.send("Enter the contents of the tag")

        contents = await self.bot.wait_for("message", check=check)

        await self.bot.db_cur.execute(
            "INSERT INTO tags(guild_id, tag, content) VALUES (?, ?, ?)",
            (
                ctx.guild.id,
                str(tname),
                str(contents),
            ),
        )
        await self.bot.db_cxn.commit()

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
        await self.bot.db_cur.execute(
            "SELECT tag FROM tags WHERE tag = ? AND guild_id = ?",
            (
                tag,
                ctx.guild.id,
            ),
        )
        result = await self.bot.db_cur.fetchone()
        if not result:
            await ctx.send(f"`{tag}`: no such tag")
            return
        await self.bot.db_cur.execute(
            "DELETE FROM tags WHERE tag = ? AND guild_id = ?",
            (
                tag,
                ctx.guild.id,
            ),
        )
        await self.bot.db_cxn.commit()

        await ctx.send(f"Tag `{tag}` successfully removed")


def setup(bot):
    bot.add_cog(Tags(bot))
