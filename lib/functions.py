from asqlite import connect
from discord.ext import commands


async def get_log_channel(ctx: commands.Context) -> int:
    async with connect("db/guild.db") as connection:
        async with connection.cursor() as cur:
            await cur.execute("SELECT log_channel_id FROM logging WHERE guild_id = ?", (ctx.guild.id,))
            result = await cur.fetchone()
            if result:
                return result[0]
