import asyncio
import traceback

import asyncpg
import discord
import yaml
from discord.ext import commands

from lib.help import VersareHelp


class Versare(commands.AutoShardedBot):
    async def get_prefix(self, message):
        if message.guild:
            prefix = self.prefixes.get(str(message.guild.id))
            if not prefix:
                return commands.when_mentioned_or(self.config["defaults"]["prefix"])(self, message)
            else:
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
            help_command=VersareHelp(),
        )

    async def on_ready(self):
        print(
            f"Versare is online - logged in as {self.user}\nClient ID: {self.user.id}\nPrefix: {self.config['defaults']['prefix']}"
        )

    def load_extensions(self):
        initial_extensions = ["cogs.commands.prefix", "cogs.listeners.error", "cogs.commands.utils"]

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                print(traceback.format_exc())

    async def setup(self):
        self.load_extensions()
        asyncio.create_task(self.init_db_pool())
        await super().setup()

    async def init_db_pool(self):
        database, pg_user, pg_password, pg_host, pg_port = list(self.config.get("postgres").values())
        self.db = await asyncpg.create_pool(dsn=f"postgres://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{database}")
        with open("db/schema.sql", "r") as init:
            await self.db.execute(init.read())
        await self.cache_prefixes()

    async def cache_prefixes(self):
        self.prefixes = await self.db.fetch("SELECT * FROM prefixes")
        self.prefixes = {str(guild_id): prefix for prefix, guild_id in self.prefixes}
