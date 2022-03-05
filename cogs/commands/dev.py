import pydoc
import sys
from inspect import getsource
from io import StringIO
from typing import Optional

import discord
from discord.ext import commands


class Developer(commands.Cog):
    """Commands for programmers"""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="source",
        aliases=["code", "command", "src", "git", "github"],
        brief="Get source code of a command or the bot",
        description="Fetch and send the source code of a bot command if specified or the GitHub repository",
    )
    async def source(
        self,
        ctx: commands.Context,
        *,
        command: Optional[str] = commands.Option(description="Specify a command:", default=None),
    ) -> discord.Message:

        if not command:
            return await ctx.send(f"Link to source code on GitHub\n{self.GITHUB_URL}/tree/{self.GIT_BRANCH}")
        elif not (cmd := self.bot.get_command(command)):
            return await ctx.send(
                f"Unknown command '{command}'. Link to source code on GitHub\n{self.GITHUB_URL}/tree/{self.GIT_BRANCH}"
            )
        elif command == "help":
            return await ctx.send(file=discord.File(self.HELP_COMMAND_FILE, filename="help.py"))
        else:
            if sys.getsizeof(buf := StringIO(getsource(cmd.callback))) > ctx.guild.filesize_limit:
                return await ctx.send(
                    f"Source code file is larger than this server's filesize limit ({ctx.guild.filesize_limit/float(1<<20):,.0f})\nThe bot's source code can be found here: {self.GITHUB_URL}/tree/{self.GIT_BRANCH}"
                )

            return await ctx.send(file=discord.File(buf, filename=command.replace(" ", "_") + ".py"))

    @commands.command(
        name="pydoc",
        brief="Get documentation for the Python standard library",
        description="Get documentation for the Python standard library",
    )
    async def pydoc(
        self,
        ctx: commands.Context,
        obj: str = commands.Option(description="What would you like to look up documentation for?"),
    ) -> discord.Message:
        if obj.split(".")[0] not in sys.stdlib_module_names or obj.startswith("_"):
            return await ctx.send(f"Object '{obj}' is not in the Python standard library")
        buf = StringIO()
        pydoc.doc(obj, output=buf)
        buf.seek(0)
        if sys.getsizeof(buf) > ctx.guild.filesize_limit:
            return await ctx.send(
                f"Documentation file is larger than this server's filesize limit ({ctx.guild.filesize_limit/float(1<<20):,.0f})"
            )
        else:
            return await ctx.send(f"Documentation for **'{obj}'**", file=discord.File(buf, filename=obj + ".py"))


def setup(bot):
    bot.add_cog(Developer(bot))
