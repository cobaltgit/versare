from random import choice, randint
from typing import Optional

import discord
from discord.ext import commands


class Games(commands.Cog):
    def __init__(self, bot):
        """Games to play"""
        self.bot = bot

    @commands.command(name="dice")
    async def dice(
        self,
        ctx,
        amount: Optional[int] = commands.Option(description="How many dice would you like to roll?", default=1),
        sides: Optional[int] = commands.Option(description="How many sides do the dice have?", default=6),
    ):
        """Roll a dice, up to 100 D20s actually"""
        if amount > 100:
            await ctx.send("You can't roll more than 100 dice at once.")
            return
        if sides > 20:
            await ctx.send("There's nothing bigger than a D20, right?")
            return
        rolls = [randint(1, sides) for _ in range(amount)]
        sumofrolls = sum(rolls)
        rollstr = ", ".join(str(roll) for roll in rolls)

        embed = discord.Embed(color=0x880000, title="Dice")
        fields = [
            ("Amount", amount, True),
            ("Rolls", rollstr, True),
            ("Sum of Rolls", sumofrolls, True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/game-die_1f3b2.png"
        )
        await ctx.send(embed=embed)

    @commands.command(name="coin", aliases=["coinflip"])
    async def coin(
        self,
        ctx,
        amount: Optional[int] = commands.Option(description="How many coins to flip?", default=1),
    ):
        """Flip a coin, or up to 100"""
        if amount > 100:
            await ctx.send("You can't flip more than 100 coins at once.")
            return

        flips = [choice(["Heads", "Tails"]) for _ in range(amount)]
        flipstr = ", ".join(flips)
        embed = discord.Embed(color=0xFFD700, title="Coin Flip")
        fields = [
            ("Amount of Coins", amount, True),
            ("Results", flipstr, True),
            ("\u200B", "\u200B", True),
            ("Amount of Heads", len(list(filter(lambda x: x == "Heads", flips))), True),
            ("Amount of Tails", len(list(filter(lambda y: y == "Tails", flips))), True),
        ]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/coin_1fa99.png"
        )
        await ctx.send(embed=embed)

    @commands.command(name="8ball")
    async def eightball(self, ctx, *, question: str = commands.Option(description="Ask the Magic 8 Ball")):
        """Ask the Magic 8-Ball and get an answer to your question"""
        responses = [
            "It is certain.",
            "It is decidedly so.",
            "Without a doubt.",
            "Yes, definitely.",
            "You may rely on it.",
            "As I see it, yes.",
            "Most likely.",
            "Outlook good.",
            "Yes.",
            "Signs point to yes.",
            "Reply hazy, try again.",
            "Ask again later.",
            "Better not tell you now.",
            "Cannot predict now.",
            "Concentrate and ask again.",
            "Don't count on it.",
            "My reply is no.",
            "My sources say no.",
            "Outlook not so good.",
            "Very doubtful.",
        ]

        embed = discord.Embed(title="The Magic 8-Ball", color=0x000080)
        fields = [("You asked:", question, True), ("Magic 8-Ball says:", choice(responses), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/pool-8-ball_1f3b1.png"
        )
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Games(bot))
