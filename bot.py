import discord
import yaml
from discord.ext import commands


class Versare(commands.AutoShardedBot):
    async def get_prefix(self, message):
        return commands.when_mentioned_or(*self.config["defaults"]["prefixes"])(self, message)

    def __init__(self):
        with open("config.yml", "r") as config_file:
            self.config = yaml.safe_load(config_file)

        super().__init__(
            command_prefix=self.get_prefix,
            intents=discord.Intents(**self.config.get("intents")),
            allowed_mentions=discord.AllowedMentions(**self.config.get("allowed-mentions")),
            slash_commands=True,
            case_sensitive=True,
            strip_after_prefix=True,
            help_command=commands.MinimalHelpCommand(),
        )

    async def on_ready(self):
        print(
            "Versare is online - logged in as %s\nClient ID: %d\nPrefixes: %s"
            % (self.user, self.user.id, self.config["defaults"]["prefixes"])
        )
