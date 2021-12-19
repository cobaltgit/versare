import json
import logging
import os
from datetime import datetime
from glob import glob
from gzip import open as gzopen
from shutil import copyfileobj as cp

import aiohttp
import asqlite
import discord
from cryptography.fernet import Fernet
from discord.ext import commands

from lib.help import VersareHelp


class Versare(commands.AutoShardedBot):
    def __init__(self):

        with open("config/config.json", "r") as config_file:
            self.config = json.load(config_file)

        self.databases = {
            "guild": {"sql": "db/guild.sql", "db": "db/guild.db"},
            "snipe": {"sql": "db/snipe.sql", "db": "db/snipe.db"},
            "tags": {"sql": "db/tags.sql", "db": "db/tags.db"},
        }

        with open("config/auth.json", "r") as auth_file:
            self.auth = json.load(auth_file)
            self.token = self.auth["token"]
            if not self.auth.get("db_encryption_key"):
                self.auth["db_encryption_key"] = str(Fernet.generate_key().decode("utf-8"))
                with open("config/auth.json", "w") as key_dump:
                    json.dump(self.auth, key_dump, indent=4)

            try:
                self.fernet = Fernet(self.auth["db_encryption_key"])
            except Exception as e:
                print(f"[FATAL] Unable to initialise Fernet encryption\n-> {type(e).__name__}: {e}")
                exit(1)

        self.init_exts = (cog.replace("/", ".")[2:-3] for cog in glob("./cogs/**/*.py"))
        self.httpsession = aiohttp.ClientSession()

        super().__init__(
            slash_commands=True,
            command_prefix=self._get_prefix,
            intents=discord.Intents(**self.config["intents"]),
            allowed_mentions=discord.AllowedMentions(**self.config["allowed_mentions"]),
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=VersareHelp(),
        )

    async def setup(self):
        if not os.path.exists("./logs"):
            os.makedirs("./logs")

        self.logpath = f'logs/discord-{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}.log'
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self.logpath, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(handler)

        async def db_init():
            self.snipe_cxn = await asqlite.connect(self.databases["snipe"]["db"])
            self.tags_cxn = await asqlite.connect(self.databases["tags"]["db"])
            self.guild_cxn = await asqlite.connect(self.databases["guild"]["db"])

            for k, v in self.databases.items():
                for connection in (self.snipe_cxn, self.tags_cxn, self.guild_cxn):
                    async with connection.cursor() as tempcursor:
                        with open(v["sql"], "r") as sql:
                            await tempcursor.executescript(sql.read())
                            await tempcursor.close()

        await db_init()

        async with self.guild_cxn.cursor() as prefix_cur:
            await prefix_cur.execute("SELECT * FROM custompfx")
            result = await prefix_cur.fetchall()
            await prefix_cur.close()
        self.prefixes = {str(guild_id): pfx for guild_id, pfx in result}
        await super().setup()

    def _get_prefix(self, bot, message):
        return commands.when_mentioned_or(
            self.prefixes[str(message.guild.id)]
            if self.prefixes.get(str(message.guild.id))
            else self.config["defaults"]["prefix"]
        )(bot, message)

    def run(self, token: str = None) -> None:
        if not token:
            raise ValueError("Please provide a valid Discord bot token")

        self.loaded_cogs = []

        for cog in self.init_exts:
            try:
                self.load_extension(cog)
                self.loaded_cogs.append(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while loading:\n-> {type(e).__name__}: {e}")

        self.load_extension("jishaku")
        super().run(token)

    async def on_ready(self):
        print(f"[{datetime.now().strftime('%d-%m-%Y %H:%M:%S')}] Bot is online")
        print(f"Logged into Discord as {self.user}")
        print(f"-> Client ID: {self.user.id}")
        print(f"-> Default Prefix: Ping or {self.config['defaults']['prefix']}")

    async def close(self):
        await self.httpsession.close()

        for cog in self.loaded_cogs:
            try:
                self.unload_extension(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while unloading:\n-> {type(e).__name__}: {e}")

        try:
            with open(self.logpath, "rb") as log:
                with gzopen(self.logpath + ".gz", "wb") as gzipped_log:
                    cp(log, gzipped_log)
            os.remove(self.logpath)
        except FileNotFoundError:
            pass

        for connection in (self.snipe_cxn, self.tags_cxn, self.guild_cxn):
            await connection.commit()
            await connection.close()

        await super().close()
