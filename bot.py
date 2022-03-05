from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import sys
import traceback
from datetime import datetime
from glob import glob
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
    def get_pfx(self, bot: commands.Bot, message: discord.Message):
        default = self.config["defaults"]["prefix"]

        if message.guild and hasattr(self, "prefixes"):
            return commands.when_mentioned_or(self.prefixes.get(message.guild.id, default))(self, message)
        else:
            return commands.when_mentioned_or(default)(self, message)

    def __init__(self) -> None:

        self.__version__ = "0.5.3"

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
            command_prefix=self.get_pfx,
            chunk_guilds_on_startup=False,
            description=f"This is Versare {self.__version__}",
            intents=discord.Intents(**self.config.get("intents")),
            allowed_mentions=discord.AllowedMentions(**self.config.get("allowed-mentions")),
            slash_commands=True,
            case_sensitive=True,
            strip_after_prefix=True,
            help_command=VersareHelp(),
        )

        self._extensions = [x.replace("/", ".")[2:-3] for x in glob("./cogs/**/*.py")]

    async def on_ready(self) -> None:
        self.start_time = time()
        print(
            f"Versare is online - logged in as {self.user}\nClient ID: {self.user.id}\nPrefix: {self.config['defaults']['prefix']}"
        )

    def load_extensions(self) -> None:
        for ext in self._extensions:
            self.load_extension(ext)

        self.load_extension("jishaku")
        self.get_command("jsk").hidden = True

    def init_logs(self) -> None:
        if not os.path.exists("./logs"):
            os.makedirs("./logs")
        self._logpath = f'logs/discord-{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}.log'
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self._logpath, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(handler)

    async def setup(self, *args, **kwargs) -> None:
        self.init_logs()
        self.HTTP_HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:10.0) Gecko/20100101 Firefox/10.0"}
        self.httpsession = aiohttp.ClientSession()
        self.load_extensions()
        asyncio.create_task(self.init_db_pool())
        await super().setup(*args, **kwargs)

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
        self.prefixes = {guild_id: prefix for prefix, guild_id in await self.db.fetch("SELECT * FROM prefixes")}

    async def close(self, *args, **kwargs) -> None:

        if hasattr(self.cogs.get("Music"), "node"):
            await self.cogs["Music"].node.disconnect()

        for ext in self._extensions:
            try:
                self.unload_extension(ext)
            except:
                print(f"Error unloading extension {ext}:\n{traceback.format_exc()}")

        if hasattr(self, "db"):
            await self.db.execute("DELETE FROM sniper")
            await self.db.execute("DELETE FROM editsniper")
            await self.db.close()

        if hasattr(self, "httpsession"):
            await self.httpsession.close()

        with contextlib.suppress(FileNotFoundError):
            with open(self._logpath, "rb") as log:
                with gzip_file(f"{self._logpath}.gz", "wb") as gzipped_log:
                    copy(log, gzipped_log)
            os.remove(self._logpath)
        await super().close(*args, **kwargs)
