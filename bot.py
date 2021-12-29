import asyncio
import os
import sys
import traceback
from time import time
import contextlib

import asyncpg
import discord
import yaml
from cryptography.fernet import Fernet
from discord.ext import commands

from utils.help import VersareHelp


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

        self.__version__ = "0.2.2-rw"

        with open("config.yml", "r") as config_file:
            self.config = yaml.safe_load(config_file)

        if not self.config["auth"].get("db_key"):
            self.config["auth"]["db_key"] = str(Fernet.generate_key().decode("utf-8"))
            with open("config.yml", "w") as config_file:
                yaml.dump(self.config, config_file, sort_keys=False)

        try:
            self.fernet = Fernet(self.config["auth"]["db_key"])
        except:
            sys.exit("Exception caught - Unable to initialise Fernet encryption key\n" + traceback.format_exc())

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
        self.start_time = time()
        print(
            f"Versare is online - logged in as {self.user}\nClient ID: {self.user.id}\nPrefix: {self.config['defaults']['prefix']}"
        )

    def load_extensions(self):
        initial_extensions = [
            "cogs.commands.prefix",
            "cogs.listeners.error",
            "cogs.commands.utils",
            "cogs.commands.mod",
            "cogs.listeners.sniper",
        ]

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except Exception:
                print(traceback.format_exc())

        os.environ["JISHAKU_HIDE"] = "true"
        self.load_extension("jishaku")

    async def setup(self):
        self.load_extensions()
        asyncio.create_task(self.init_db_pool())
        await super().setup()

    async def init_db_pool(self):
        database, pg_user, pg_password, pg_host, pg_port = self.config.get("postgres").values()
        await self.wait_until_ready()
        try:
            self.db = await asyncpg.create_pool(dsn=f"postgres://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{database}")
        except:
            sys.exit(f"Couldn't connect to PostgreSQL database server\n{traceback.format_exc()}")
        else:
            with open("db/schema.sql", "r") as init:
                await self.db.execute(init.read())
            await self.cache_prefixes()

    async def cache_prefixes(self):
        self.prefixes = await self.db.fetch("SELECT * FROM prefixes")
        self.prefixes = {str(guild_id): prefix for prefix, guild_id in self.prefixes}

    async def close(self):
        with contextlib.suppress(AttributeError):
            await self.db.execute("DELETE FROM sniper")
            await self.db.execute("DELETE FROM editsniper")
        await super().close()
