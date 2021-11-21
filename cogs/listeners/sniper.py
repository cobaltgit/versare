from asyncio import sleep as aiosleep

import discord
from discord.ext import commands


class Sniper(commands.Cog):
    """on_message listener for snipe command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        self.bot.db_cur.execute("DELETE FROM sniper WHERE channel_id = ?", (message.channel.id,))

        self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (message.guild.id,))
        optout_uids = self.bot.db_cur.fetchone()
        if optout_uids is not None and message.author.id in optout_uids:
            return

        msg = message.content.encode()
        self.encrypted_msg = self.bot.fernet.encrypt(msg)

        self.bot.db_cur.execute(
            "INSERT INTO sniper(message, author_id, channel_id) VALUES (?,?,?)",
            (
                self.encrypted_msg,
                message.author.id,
                message.channel.id,
            ),
        )
        self.bot.db_cxn.commit()
        await aiosleep(60)
        self.bot.db_cur.execute("DELETE FROM sniper")
        self.bot.db_cxn.commit()


def setup(bot):
    bot.add_cog(Sniper(bot))
