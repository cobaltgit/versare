from asyncio import sleep as aiosleep

import discord
from discord.ext import commands


class Sniper(commands.Cog):
    """on_message listener for snipe command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        await self.bot.db_cur.execute("DELETE FROM sniper WHERE channel_id = ?", (message.channel.id,))

        await self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (message.guild.id,))
        optout_uids = await self.bot.db_cur.fetchone()
        if optout_uids is not None and message.author.id in optout_uids:
            return

        msg = message.content.encode()
        self.encrypted_msg = self.bot.fernet.encrypt(msg)

        await self.bot.db_cur.execute(
            "INSERT INTO sniper(message, author_id, channel_id) VALUES (?,?,?)",
            (
                self.encrypted_msg,
                message.author.id,
                message.channel.id,
            ),
        )
        await self.bot.db_cxn.commit()
        await aiosleep(60)
        await self.bot.db_cur.execute("DELETE FROM sniper")
        await self.bot.db_cxn.commit()

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        await self.bot.db_cur.execute("DELETE FROM editsniper WHERE channel_id = ?", (before.channel.id,))

        await self.bot.db_cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (before.guild.id,))
        optout_uids = await self.bot.db_cur.fetchone()
        if optout_uids is not None and before.author.id in optout_uids:
            return

        before_msg = before.content.encode()
        after_msg = after.content.encode()
        self.encrypted_msg_before = self.bot.fernet.encrypt(before_msg)
        self.encrypted_msg_after = self.bot.fernet.encrypt(after_msg)

        await self.bot.db_cur.execute(
            "INSERT INTO editsniper(message_before, message_after, author_id, channel_id) VALUES (?,?,?,?)",
            (
                self.encrypted_msg_before,
                self.encrypted_msg_after,
                before.author.id,
                before.channel.id,
            ),
        )
        await self.bot.db_cxn.commit()
        await aiosleep(60)
        await self.bot.db_cur.execute("DELETE FROM editsniper")
        await self.bot.db_cxn.commit()


def setup(bot):
    bot.add_cog(Sniper(bot))
