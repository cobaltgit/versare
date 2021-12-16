from asyncio import sleep as aiosleep

import discord
from discord.ext import commands


class Sniper(commands.Cog):
    """on_message listener for snipe command"""

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("DELETE FROM sniper WHERE channel_id = ?", (message.channel.id,))

            await cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (message.guild.id,))
            optout_uids = await cur.fetchone()
            if optout_uids is not None and message.author.id in optout_uids:
                return

            self.encrypted_msg = self.bot.fernet.encrypt(message.content.encode())

            await cur.execute(
                "INSERT INTO sniper(message, author_id, channel_id) VALUES (?,?,?)",
                (
                    self.encrypted_msg,
                    message.author.id,
                    message.channel.id,
                ),
            )
            await self.bot.snipe_cxn.commit()
            await cur.close()
        await aiosleep(60)
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("DELETE FROM sniper WHERE channel_id = ?", (message.channel.id,))
            await self.bot.snipe_cxn.commit()
            await cur.close()
        try:
            del self.encrypted_msg
        except AttributeError:
            pass

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("DELETE FROM editsniper WHERE channel_id = ?", (before.channel.id,))

            await cur.execute("SELECT user_id FROM sniper_optout WHERE guild_id = ?", (before.guild.id,))
            optout_uids = await cur.fetchone()
            if optout_uids is not None and before.author.id in optout_uids:
                return

            self.encrypted_msg_before = self.bot.fernet.encrypt(before.content.encode())
            self.encrypted_msg_after = self.bot.fernet.encrypt(after.content.encode())

            await cur.execute(
                "INSERT INTO editsniper(message_before, message_after, author_id, channel_id) VALUES (?,?,?,?)",
                (
                    self.encrypted_msg_before,
                    self.encrypted_msg_after,
                    before.author.id,
                    before.channel.id,
                ),
            )
            await self.bot.snipe_cxn.commit()
            await cur.close()
            await aiosleep(60)
        async with self.bot.snipe_cxn.cursor() as cur:
            await cur.execute("DELETE FROM editsniper WHERE channel_id = ?", (before.channel.id,))
            await self.bot.snipe_cxn.commit()
            await cur.close()
        try:
            del self.encrypted_msg_before
            del self.encrypted_msg_after
        except AttributeError:
            pass


def setup(bot):
    bot.add_cog(Sniper(bot))
