from discord.ext import commands
from thefuzz import fuzz


class ErrorHandler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f"Required argument `{error.param}` missing.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(
                f":hourglass: | Cooldown - you can run command `{ctx.command}` after {round(error.retry_after, 1)} seconds."
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
            prefix = self.bot.guildpfx if not self.bot.user.mentioned_in(ctx.message) else f"<@!{self.bot.user.id}>"
            available_commands = [command.name for command in self.bot.walk_commands()]
            ratios = [
                fuzz.ratio(ctx.message.content[len(self.bot.guildpfx) :], command) for command in available_commands
            ]
            closest_match = available_commands[ratios.index(max(ratios))]
            await ctx.send(
                f""":x: | Command `{ctx.message.content[len(prefix):].split()[0]}` not found.
Maybe you meant `{closest_match}`?"""
            )

        else:
            raise error


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
