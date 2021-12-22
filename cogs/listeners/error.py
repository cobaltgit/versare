import traceback

from discord.ext import commands

from lib.views import Traceback


class ErrorHandler(commands.Cog):
    """Universal error handler"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.CommandInvokeError):
            error = error.original
            await ctx.send(
                "Exception caught",
                view=Traceback(ctx, "".join(traceback.format_exception(type(error), error, error.__traceback__))),
            )
        else:
            raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
