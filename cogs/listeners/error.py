from discord.ext import commands


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Required argument `{error.param}` missing.")
        elif isinstance(error, commands.CommandOnCooldown):
            if ctx.author.id == self.bot.config["owner_id"]:
                return await ctx.reinvoke()
            await ctx.send(
                f":hourglass: | Cooldown - you can run command `{ctx.command}` after {round(error.retry_after, 1)} seconds."
            )
        elif isinstance(error, commands.ConversionError):
            await ctx.send(f"Conversion error: {error}")
        elif isinstance(error, commands.BotMissingPermissions):
            missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
            fmt = (
                "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
                if len(missing) > 2
                else " and ".join(missing)
            )
            await ctx.send(f"I am missing **{fmt}** permission(s) needed to run this command.")
        elif isinstance(error, commands.MissingPermissions):
            missing = [perm.replace("_", " ").replace("guild", "server").title() for perm in error.missing_permissions]
            fmt = (
                "{}, and {}".format("**, **".join(missing[:-1]), missing[-1])
                if len(missing) > 2
                else " and ".join(missing)
            )
            await ctx.send(f"You are missing **{fmt}** permission(s) needed to run this command.")
        elif isinstance(error, commands.DisabledCommand):
            await ctx.send(f"`{ctx.command}` has been disabled.")
        elif isinstance(error, commands.CheckFailure):
            return
        else:
            raise error
        return


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
