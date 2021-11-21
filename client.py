import json
import logging
import os
import sqlite3
from datetime import datetime
from glob import glob
from gzip import open as gzopen
from shutil import copyfileobj as cp

import aiohttp
import discord
from discord.ext import commands


class Versare(commands.AutoShardedBot):

    db_cxn = sqlite3.connect("./db/bot.db")
    db_cur = db_cxn.cursor()

    def __init__(self):

        if not os.path.exists("./logs"):
            os.makedirs("./logs")

        with open("config/config.json", "r") as config_file:
            self.config = json.load(config_file)
            config_file.close()

        with open("config/auth.json", "r") as token_file:
            self.token = json.load(token_file)["token"]
            token_file.close()

        self.init_exts = (cog.replace("/", ".")[2:-3] for cog in glob("./cogs/**/*.py"))

        def _get_prefix(bot, message):
            self.db_cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (message.guild.id,))
            result = self.db_cur.fetchone()
            self.guildpfx = self.config["defaults"]["prefix"] if result is None else str(result[0])
            return commands.when_mentioned_or(self.guildpfx)(bot, message)

        super().__init__(
            slash_commands=True,
            command_prefix=_get_prefix,
            intents=discord.Intents(**self.config["intents"]),
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=commands.MinimalHelpCommand(),
        )

    def run(self, token: str = None) -> None:
        if not token:
            raise ValueError("Please provide a valid Discord bot token")

        self.logpath = f'logs/discord-{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}.log'
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self.logpath, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(handler)

        self.loaded_cogs = []

        with open("./db/init.sql", "r") as db_init:
            self.db_cur.executescript(db_init.read())
            db_init.close()

        for cog in self.init_exts:
            try:
                self.load_extension(cog)
                self.loaded_cogs.append(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while loading:\n-> {type(e).__name__}: {e}")

        self.httpsession = aiohttp.ClientSession()
        self.load_extension("jishaku")

        super().run(token)

    async def on_ready(self):
        start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"[{start_time}]")
        print(f"Logged into Discord as {self.user}")
        print(f"-> Client ID: {self.user.id}")
        print(
            f"-> Default Prefix: Ping or {self.config['defaults']['prefix']}"
            if self.config.get("ping_prefix", False)
            else f"-> Default Prefix: {self.config['defaults']['prefix']}"
        )

    async def close(self):
        await self.httpsession.close()

        for cog in self.loaded_cogs:
            try:
                self.unload_extension(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while unloading:\n-> {type(e).__name__}: {e}")

        self.db_cxn.commit()
        self.db_cur.close()
        self.db_cxn.close()

        try:
            with open(self.logpath, "rb") as log:
                with gzopen(self.logpath + ".gz", "wb") as gzipped_log:
                    cp(log, gzipped_log)
            os.remove(self.logpath)
        except FileNotFoundError:
            pass

        await super().close()
