from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Required argument `{error.param}` missing.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f":stopwatch Cooldown: you can run command `{ctx.command}` after {round(error.retry_after, 1)} seconds."
            )
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error: {error}")
        elif isinstance(error, commands.MissingPermissions):
            await ctx.send(f"Permission denied: {error}")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"`{ctx.command}` has been disabled.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send(
                f"Permissions check for command `{ctx.command}` failed - this command may only work if you are the bot owner or have administrator permissions.."
            )
        elif isinstance(error, commands.CommandNotFound):
            return
        else:
            raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
