import asyncio
from random import choice

import discord
from discord.ext import commands

from utils.objects import BaseEmbed
from utils.views import Wordle


class Games(commands.Cog):
    """Fun games to play"""

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        with open("./utils/files/wordle_dict.txt") as f:  # word list from
            self.WORDLE_DICT = list(map(str.strip, f.readlines()))

    @commands.command(
        name="wordle", aliases=["lingo"], brief="Play Wordle", description="Play Wordle, the hit word guessing game"
    )
    async def wordle(self, ctx: commands.Context) -> discord.Message:

        matrix = ["\U00002b1c" * 5 for _ in range(6)]
        embed = BaseEmbed(title="Wordle", description="\n".join(matrix), color=ctx.author.color)
        embed.set_author(icon_url=ctx.author.avatar.url, name=ctx.author.name)

        view = Wordle(word=choice(self.WORDLE_DICT))
        msg = await ctx.send(embed=embed, view=view)

        guesses = 6

        while guesses and ("\U0001f7e9" * 5) not in matrix:
            try:
                user_word = await self.bot.wait_for(
                    "message", check=lambda m: m.author == ctx.author and m.channel == ctx.channel
                )
            except asyncio.TimeoutError:
                return await ctx.send("Game timed out!") if not view.is_finished() else False

            if view.is_finished():
                return

            if user_word.content not in self.WORDLE_DICT:
                await ctx.send(
                    "This word isn't in the accepted word list! This doesn't count towards your guess limit, so don't worry and try again!",
                    reference=user_word,
                    delete_after=3,
                )
            else:
                greens = [u == w for u, w in zip(user_word.content, view.word)]
                leftover = [w for w, g in zip(view.word, greens) if not g]
                yellows = []
                for u, g in zip(user_word.content, greens):
                    if not g and u in leftover:
                        leftover.remove(u)
                        yellows.append(True)
                    else:
                        yellows.append(False)
                matrix[-guesses] = "".join(
                    "\U0001f7e9" if greens[i] else "\U0001f7e7" if not greens[i] and yellows[i] else "\U00002b1c"
                    for i in range(len(user_word.content))
                )
                embed.description = "\n".join(matrix)
                await msg.edit(embed=embed)
                guesses -= 1

            if user_word.content == view.word:
                break

        view.stop()
        if ("\U0001f7e9" * 5) in matrix:
            return await ctx.send(f"Well done, you got it right, with {guesses} guesses to spare!")
        else:
            return await ctx.send(f"Better luck next time, the correct word was '{view.word}'")


def setup(bot: commands.Bot) -> None:
    bot.add_cog(Games(bot))
