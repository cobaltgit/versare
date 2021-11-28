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


class Versare(commands.AutoShardedBot):
    def __init__(self):

        if not os.path.exists("./logs"):
            os.makedirs("./logs")

        with open("config/config.json", "r") as config_file:
            self.config = json.load(config_file)

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

        super().__init__(
            slash_commands=True,
            command_prefix=self._get_prefix,
            intents=discord.Intents(**self.config["intents"]),
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=commands.MinimalHelpCommand(),
        )

    async def setup(self):
        await self.db_cur.execute("SELECT * FROM custompfx")
        result = await self.db_cur.fetchall()
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

        self.logpath = f'logs/discord-{datetime.now().strftime("%d-%m-%Y-%H:%M:%S")}.log'
        self.logger = logging.getLogger("discord")
        self.logger.setLevel(logging.DEBUG)
        handler = logging.FileHandler(filename=self.logpath, encoding="utf-8", mode="w")
        handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
        self.logger.addHandler(handler)

        self.loaded_cogs = []

        for cog in self.init_exts:
            try:
                self.load_extension(cog)
                self.loaded_cogs.append(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while loading:\n-> {type(e).__name__}: {e}")

        self.httpsession = aiohttp.ClientSession()
        self.load_extension("jishaku")

        async def db_init():
            self.db_cxn = await asqlite.connect("db/versare.db")
            self.db_cur = await self.db_cxn.cursor()
            await self.db_cur.executescript(open("db/init.sql", "r").read())

        self.loop.run_until_complete(db_init())
        super().run(token)

    async def on_ready(self):
        start_time = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
        print(f"[{start_time}]")
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

        if os.path.exists("db/versare.db"):
            await self.db_cur.execute("DELETE FROM sniper")
            await self.db_cur.execute("DELETE FROM editsniper")
            await self.db_cxn.commit()
            await self.db_cur.close()
            await self.db_cxn.close()

        try:
            with open(self.logpath, "rb") as log:
                with gzopen(self.logpath + ".gz", "wb") as gzipped_log:
                    cp(log, gzipped_log)
            os.remove(self.logpath)
        except FileNotFoundError:
            pass

        await super().close()
