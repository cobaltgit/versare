import json
import sqlite3
from datetime import datetime
from glob import glob

import aiohttp
import discord
from discord.ext import commands


class Versare(commands.AutoShardedBot):

    db_cxn = sqlite3.connect("./db/bot.db")
    db_cur = db_cxn.cursor()

    def __init__(self):

        with open("config.json", "r") as config_file:
            self.config = json.load(config_file)
            config_file.close()

        self.exts = [cog.replace("/", ".")[2:-3] for cog in glob("./cogs/**/*.py")]

        def _get_prefix(bot, message):
            self.db_cur.execute("SELECT prefix FROM custompfx WHERE guild_id = ?", (message.guild.id,))
            result = self.db_cur.fetchone()
            return commands.when_mentioned_or(self.config["defaults"]["prefix"] if result is None else str(result[0]))(
                bot, message
            )

        super().__init__(
            slash_commands=True,
            command_prefix=_get_prefix,
            intents=discord.Intents(**self.config["intents"]),
            case_insensitive=True,
            strip_after_prefix=True,
            help_command=commands.MinimalHelpCommand(),
        )

    def run(self, token: str = None) -> None:
        if token is None:
            raise ValueError("Please provide a valid Discord bot token")

        self.loaded_cogs = []

        with open("./db/init.sql", "r") as db_init:
            self.db_cur.executescript(db_init.read())
            db_init.close()

        for cog in self.exts:
            try:
                self.load_extension(cog)
                self.loaded_cogs.append(cog)
            except Exception as e:
                print(f"[ERR] Cog `{cog}` raised an exception while loading:\n-> {type(e).__name__}: {e}")

        self.httpsession = aiohttp.ClientSession()

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

        await super().close()
