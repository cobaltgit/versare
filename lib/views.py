from datetime import datetime
from random import choice
from typing import TYPE_CHECKING, Any, Generator, List

import discord
from discord.ext import commands
from discord.ui import View, button


class RPSView(View):
    def __init__(self, ctx):
        self.ctx = ctx
        self.user = self.ctx.author
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
        if interaction.user != self.user:
            return
        return await self.process("rock")

    @button(label="Paper", style=discord.ButtonStyle.green, emoji="📄")
    async def callback2(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        return await self.process("paper")

    @button(label="Scissors", style=discord.ButtonStyle.blurple, emoji="✂️")
    async def callback3(self, button: discord.ui.Button, interaction: discord.Interaction):
        if interaction.user != self.user:
            return
        return await self.process("scissors")

    async def on_timeout(self):
        await self.ctx.send("Game timeout reached", ephemeral=True)
        await self.message.delete()
        self.stop()


class BaseButtonPaginator(discord.ui.View):
    """
    The Base Button Paginator class. Will handle all page switching without
    you having to do anything.

    Attributes
    ----------
    entries: List[Any]
        A list of entries to get spread across pages.
    per_page: :class:`int`
        The number of entries that get passed onto one page.
    pages: List[List[Any]]
        A list of pages which contain all entries for that page.
    """

    if TYPE_CHECKING:
        ctx: commands.Context

    def __init__(self, *, entries: List[Any], per_page: int = 6) -> None:
        super().__init__(timeout=180)
        self.entries = entries
        self.per_page = per_page

        self._min_page = 1
        self._current_page = 1
        self.pages = list(self._format_pages(entries, per_page))
        self._max_page = len(self.pages)

    @property
    def max_page(self) -> int:
        """:class:`int`: The max page count for this paginator."""
        return self._max_page

    @property
    def min_page(self) -> int:
        """:class:`int`: The min page count for this paginator."""
        return self._min_page

    @property
    def current_page(self) -> int:
        """:class:`int`: The current page the user is on."""
        return self._current_page

    @property
    def total_pages(self) -> int:
        """:class:`int`: Returns the total amount of pages."""
        return len(self.pages)

    async def format_page(self, entries: List[Any]) -> discord.Embed:
        """|coro|

        Used to make the embed that the user sees.

        Parameters
        ----------
        entries: List[Any]
            A list of entries for the current page.

        Returns
        -------
        :class:`discord.Embed`
            The embed for this page.
        """
        raise NotImplementedError("Subclass did not overwrite format_page coro.")

    def _format_pages(self, entries, total_pgs) -> Generator[List[Any], None, None]:
        for i in range(0, len(entries), total_pgs):
            yield entries[i : i + total_pgs]

    def _get_entries(self, *, up: bool = True, increment: bool = True) -> List[Any]:
        if increment:
            if up:
                self._current_page += 1
                if self._current_page > self._max_page:
                    self._current_page = self._min_page
            else:
                self._current_page -= 1
                if self._current_page < self._min_page:
                    self._current_page = self.max_page

        return self.pages[self._current_page - 1]

    @discord.ui.button(emoji="\U000025c0", style=discord.ButtonStyle.blurple)
    async def on_arrow_backward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        entries = self._get_entries(up=False)
        embed = await self.format_page(entries=entries)
        return await interaction.response.edit_message(embed=embed)

    @discord.ui.button(emoji="\U000025b6", style=discord.ButtonStyle.blurple)
    async def on_arrow_forward(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        entries = self._get_entries(up=True)
        embed = await self.format_page(entries=entries)
        return await interaction.response.edit_message(embed=embed)

    @discord.ui.button(emoji="\U000023f9", style=discord.ButtonStyle.blurple)
    async def on_stop(self, button: discord.ui.Button, interaction: discord.Interaction) -> None:
        self.clear_items()
        self.stop()
        return await interaction.response.edit_message(view=self)

    @classmethod
    async def start(cls, context: commands.Context, *, entries: List[Any], per_page: int = 6):
        """|coro|

        Used to start the paginator.

        Parameters
        ----------
        context: :class:`commands.Context`
            The context to send to. This could also be discord.abc.Messageable as `ctx.send` is the only method
            used.
        entries: List[Any]
            A list of entries to pass onto the paginator.
        per_page: :class:`int`
            A number of how many entries you want per page.
        """
        new = cls(entries=entries, per_page=per_page)
        new.ctx = context

        entries = new._get_entries(increment=False)
        embed = await new.format_page(entries=entries)
        await context.send(embed=embed, view=new)


class TagSearchPaginator(BaseButtonPaginator):
    def __init__(self, entries: List[Any], *, per_page: int = 6):
        super().__init__(entries=entries, per_page=per_page)

    async def format_page(self, entries):
        return discord.Embed(
            title="Tag Search",
            description="\n".join([f"{idx}. {entry}" for idx, entry in enumerate(entries)]),
            timestamp=datetime.utcnow(),
        )
