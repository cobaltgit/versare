import os
from datetime import datetime
from gzip import open as gzopen
from shutil import copyfileobj as cp
from sqlite3 import connect

from discord.ext import commands, tasks


class ScheduledTasks(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tasks = [self.backupdb_scheduled]

    def db_dump(self, dump_path):
        """
        asqlite has no iterdump function, so we have to convert this function to async with loop.run_in_executor (see line 48)
        Dumps the database with a temporary connection and compresses it with gzip
        """

        with open(dump_path, "w") as dump:
            dump.writelines(connect("db/versare.db").iterdump())

        with open(dump_path, "rb") as dump:
            with gzopen(dump_path + ".gz", "wb") as gzipped_dump:
                cp(dump, gzipped_dump)
        os.remove(dump_path)

    @tasks.loop(hours=24)
    async def backupdb_scheduled(self):
        """Back up the bot's database"""

        if not self.bot.config.get("db_dump_path", False):
            print(
                f"[{datetime.now().strftime('%d-%M-%Y %H:%M:%S')}] Scheduled database backup skipped due to dump path being unset.\n-> Set the database dump path in the bot's config.json file, located in the config directory."
            )
            return

        dump_path = os.path.join(
            self.bot.config["db_dump_path"],
            f"versare-{datetime.now().strftime('%d-%m-%Y')}.sql",
        )

        if not os.path.exists(dump_path.rsplit("/", 1)[0]):
            os.makedirs(dump_path.rsplit("/", 1)[0])

        await self.bot.db_cur.execute("DELETE FROM sniper")
        await self.bot.db_cur.execute("DELETE FROM editsniper")
        await self.bot.db_cxn.commit()

        self.bot.loop.run_in_executor(None, self.db_dump, dump_path)

        print(f"[{datetime.now().strftime('%d-%M-%Y %H:%M:%S')}] Scheduled database backup completed")

    @commands.Cog.listener()
    async def on_ready(self):
        for task in self.tasks:
            task.start()


def setup(bot):
    bot.add_cog(ScheduledTasks(bot))
