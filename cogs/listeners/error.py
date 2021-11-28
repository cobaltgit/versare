import discord
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
            await ctx.send(
                f"Permissions check for command `{ctx.command}` failed - this command may only work if you are the bot owner or have administrator permissions."
            )
        elif isinstance(error, commands.CommandNotFound):
            prefix = self.bot.guildpfx if not self.bot.user.mentioned_in(ctx.message) else f"<@!{self.bot.user.id}>"
            available_commands = [command.name for command in self.bot.commands]
            ratios = [fuzz.ratio(ctx.message.content[len(prefix) :], command) for command in available_commands]
            closest_match = available_commands[ratios.index(max(ratios))]
            await ctx.send(
                f""":x: | Command `{ctx.message.content[len(prefix):].split()[0]}` not found.
Maybe you meant `{closest_match}`?"""
            )
        elif isinstance(error, commands.UserInputError):
            await ctx.send("Invalid user input")
            await self.send_command_help(ctx)

        else:
            raise error
        return

    @commands.Cog.listener()
    async def on_message(self, message):
        if isinstance(message.channel, discord.DMChannel):
            await message.channel.send("Commands cannot be used in DMs")
            return


def setup(bot):
    bot.add_cog(ErrorHandler(bot))
