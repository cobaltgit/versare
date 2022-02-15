from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import sys
import traceback
from datetime import datetime
from gzip import open as gzip_file
from shutil import copyfileobj as copy
from time import time

import aiohttp
import asyncpg
import discord
import yaml
from cryptography.fernet import Fernet
from discord.ext import commands

from utils.help import VersareHelp


class Versare(commands.AutoShardedBot):
    @property
    def loaded_extensions(self) -> list[str]:
        return self._loaded_extensions

    async def get_prefix(self, message: discord.Message) -> function:
        if not message.guild:
            return commands.when_mentioned_or(self.config["defaults"]["prefix"])(self, message)
        try:
            prefix = self.prefixes.get(str(message.guild.id))
        except AttributeError:
            return commands.when_mentioned_or(self.config["defaults"]["prefix"])(self, message)
        if not prefix:
            return commands.when_mentioned_or(self.config["defaults"]["prefix"])(self, message)
        else:
            return commands.when_mentioned_or(prefix)(self, message)

    def __init__(self) -> None:

        self.__version__ = "0.4.6-rw"

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
            chunk_guilds_on_startup=False,
            description=f"This is Versare {self.__version__}",
            intents=discord.Intents(**self.config.get("intents")),
            allowed_mentions=discord.AllowedMentions(**self.config.get("allowed-mentions")),
            slash_commands=True,
            case_sensitive=True,
            strip_after_prefix=True,
            help_command=VersareHelp(),
        )

    async def on_ready(self) -> None:
        self.start_time = time()
        print(
            f"Versare is online - logged in as {self.user}\nClient ID: {self.user.id}\nPrefix: {self.config['defaults']['prefix']}"
        )

    def load_extensions(self) -> None:
        initial_extensions = [
            "cogs.commands.prefix",
            "cogs.listeners.error",
            "cogs.commands.utils",
            "cogs.commands.mod",
            "cogs.listeners.sniper",
            "cogs.commands.inet",
            "cogs.listeners.token",
            "cogs.commands.music",
        ]
        self._loaded_extensions = []

        for ext in initial_extensions:
            try:
                self.load_extension(ext)
            except:
                print(f"Error loading extension {ext}:\n{traceback.format_exc()}")
            else:
                self._loaded_extensions.append(ext)

        os.environ["JISHAKU_HIDE"] = "true"
        self.load_extension("jishaku")

    def init_logs(self) -> None:
        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        self._logpath = f'logs/discord-{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}.log'
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self._logpath, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(handler)

    async def setup(self) -> None:
        self.init_logs()
        self.HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"}
        self.httpsession = aiohttp.ClientSession()
        self.load_extensions()
        asyncio.create_task(self.init_db_pool())
        await super().setup()

    async def init_db_pool(self) -> None:
        database, pg_user, pg_password, pg_host, pg_port = self.config.get("postgres").values()
        await self.wait_until_ready()
        try:
            self.db = await asyncpg.create_pool(
                dsn=f"postgres://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{database}"
            )
        except:
            sys.exit(f"Couldn't connect to PostgreSQL database server\n{traceback.format_exc()}")
        else:
            with open("db/schema.sql", "r") as init:
                await self.db.execute(init.read())
            await self.cache_prefixes()

    async def cache_prefixes(self) -> None:
        self.prefixes = {str(guild_id): prefix for prefix, guild_id in await self.db.fetch("SELECT * FROM prefixes")}

    async def close(self, *args, **kwargs) -> None:

        with contextlib.suppress(AttributeError):
            await self.cogs["Music"].node.disconnect()

        for ext in self.loaded_extensions:
            try:
                self.unload_extension(ext)
            except:
                print(f"Error unloading extension {ext}:\n{traceback.format_exc()}")
            else:
                self._loaded_extensions.remove(ext)

        with contextlib.suppress(AttributeError, FileNotFoundError):
            await self.db.execute("DELETE FROM sniper")
            await self.db.execute("DELETE FROM editsniper")
            await self.db.close()
            await self.httpsession.close()
            with open(self._logpath, "rb") as log:
                with gzip_file(f"{self._logpath}.gz", "wb") as gzipped_log:
                    copy(log, gzipped_log)
            os.remove(self._logpath)
        await super().close(*args, **kwargs)
