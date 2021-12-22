import asyncio

import asyncpg
import discord
import yaml
from discord.ext import commands


class Versare(commands.AutoShardedBot):
    async def get_prefix(self, message):
        if message.guild:
            prefix = await self.db.fetchval("SELECT prefix FROM prefixes WHERE guild_id = $1", message.guild.id)
            if not prefix:
                await self.db.execute(
                    "INSERT INTO prefixes (guild_id, prefix) VALUES ($1, $2)",
                    message.guild.id,
                    self.config["defaults"]["prefix"],
                )
            return commands.when_mentioned_or(prefix)(self, message)
        else:
            return commands.when_mentioned_or(self.config["defaults"]["prefix"])(self, message)

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
            "Versare is online - logged in as %s\nClient ID: %d\nPrefix: %s"
            % (self.user, self.user.id, self.config["defaults"]["prefix"])
        )

    async def setup(self):
        asyncio.create_task(self.init_db_pool())
        await super().setup()

    async def init_db_pool(self):
        database, pg_user, pg_password, pg_host, pg_port = list(self.config.get("postgres").values())
        self.db = await asyncpg.create_pool(dsn=f"postgres://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{database}")
        with open("db/schema.sql", "r") as init:
            await self.db.execute(init.read())
