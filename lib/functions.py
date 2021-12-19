import discord
from asqlite import connect


async def get_log_channel(guild: discord.Guild) -> int:
    async with connect("db/guild.db") as connection:
        async with connection.cursor() as cur:
            await cur.execute("SELECT log_channel_id FROM logging WHERE guild_id = ?", (guild.id,))
            result = await cur.fetchone()
            if result:
                return result[0]
