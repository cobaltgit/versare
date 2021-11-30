from datetime import datetime
from random import choice, randint
from typing import Optional

import discord
from discord.ext import commands
from discord.ui import View, button


class RPSView(View):
    def __init__(self, ctx):
        self.ctx = ctx
        super().__init__(timeout=15)

    async def process(self, rps_user: str):
        rps_cpu = choice(["rock", "paper", "scissors"])
        checks = {
            ("rock", "scissors"): "win",
            ("scissors", "rock"): "loss",
            ("paper", "scissors"): "loss",
            ("paper", "rock"): "win",
            ("rock", "paper"): "loss",
            ("scissors", "paper"): "win",
        }
        result = checks[(rps_user, rps_cpu)] if rps_user != rps_cpu else "draw"
        if result == "win":
            embed = discord.Embed(title="You won!", color=0x50C878, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/trophy_1f3c6.png"
            )
        elif result == "loss":
            embed = discord.Embed(title="You lost!", color=0xD22B2B, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/stop-sign_1f6d1.png"
            )
        elif result == "draw":
            embed = discord.Embed(title="It's a tie!", color=0xFFBF00, timestamp=datetime.utcnow())
            emoji_url = (
                "https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/120/twitter/282/necktie_1f454.png"
            )
        fields = [("Your choice", rps_user.title(), True), ("CPU's choice", rps_cpu.title(), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(url=emoji_url)
        await self.message.edit(embed=embed, view=None)
        self.stop()

    @button(label="Rock", style=discord.ButtonStyle.red, emoji="🪨")
    async def callback1(self, button: discord.ui.Button, interaction: discord.Interaction):
        return await self.process("rock")

    @button(label="Paper", style=discord.ButtonStyle.green, emoji="📄")
    async def callback2(self, button: discord.ui.Button, interaction: discord.Interaction):
        return await self.process("paper")

    @button(label="Scissors", style=discord.ButtonStyle.blurple, emoji="✂️")
    async def callback3(self, button: discord.ui.Button, interaction: discord.Interaction):
        return await self.process("scissors")

    async def on_timeout(self):
        await self.ctx.send("Game timeout reached")
        self.stop()


class Games(commands.Cog):
    def __init__(self, bot):
        """Games to play"""
        self.bot = bot
        self.ball_responses = (
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
        )

    @commands.command(name="dice", brief="Roll some dice", description="Roll up to 100 dice with 20 sides")
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

        embed = discord.Embed(color=0x880000, title="Dice", timestamp=datetime.utcnow())
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

    @commands.command(
        name="coin",
        aliases=["coinflip"],
        brief="Flip a coin and get heads or tails, up to 100 actually",
        description="Flip up to 100 coins at once",
    )
    async def coin(
        self,
        ctx,
        amount: Optional[int] = commands.Option(description="How many coins to flip?", default=1),
    ):
        """Flip a coin, or up to 100"""
        if amount > 100:
            return await ctx.send("You can't flip more than 100 coins at once.")

        flips = [choice(["Heads", "Tails"]) for _ in range(amount)]
        flipstr = ", ".join(flips)
        embed = discord.Embed(color=0xFFD700, title="Coin Flip", timestamp=datetime.utcnow())
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

    @commands.command(
        name="8ball",
        brief="Ask the Magic 8-Ball",
        description="Ask the future-foreseeing Magic 8-Ball and get the answer to your question",
    )
    async def eightball(self, ctx, *, question: str = commands.Option(description="Ask the Magic 8 Ball")):
        """Ask the Magic 8-Ball and get an answer to your question"""
        embed = discord.Embed(title="The Magic 8-Ball", color=0x000080, timestamp=datetime.utcnow())
        fields = [("You asked:", question, True), ("Magic 8-Ball says:", choice(self.ball_responses), True)]
        for name, value, inline in fields:
            embed.add_field(name=name, value=value, inline=inline)
        embed.set_thumbnail(
            url="https://emojipedia-us.s3.dualstack.us-west-1.amazonaws.com/thumbs/160/twitter/282/pool-8-ball_1f3b1.png"
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="rps",
        aliases=["janken"],
        brief="Play rock, paper, scissors!",
        description="Play rock, paper, scissors with the bot",
    )
    async def rps(self, ctx):
        """Play rock, paper, scissors with the bot"""
        embed = discord.Embed(
            title="Rock, Paper, Scissors!",
            description="Pick one of the buttons below",
            color=ctx.author.color,
            timestamp=datetime.utcnow(),
        )
        embed.set_image(url="https://c.tenor.com/7HFPLm7Rl8oAAAAC/321-count-down.gif")

        view = RPSView(ctx)
        view.message = await ctx.send(embed=embed, view=view)


def setup(bot):
    bot.add_cog(Games(bot))
