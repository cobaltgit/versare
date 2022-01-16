import discord
from youtube_dl import YoutubeDL


def nitro_check(user: discord.User | discord.Member) -> bool:
    """Guesses if a user has Nitro from a set of attributes and features.
    The Member.nitro attribute was removed in discord.py 1.7, so there is no official way to check if a user has Nitro for definite

    Args:
        user (discord.User|discord.Member): the user to query

    Returns:
        bool: evaluates if the user exhibits any of the Nitro features
    """
    if isinstance(user, discord.Member):
        has_emote_status = any(a.emoji.is_custom_emoji() for a in user.activities if hasattr(a, "emoji"))

        return any([user.display_avatar.is_animated(), has_emote_status, user.premium_since, user.guild_avatar])
    return any([user.display_avatar.is_animated(), user.banner])


def get_youtube_url(source_url: str, ydl_opts: dict[str] = {"quiet": True}) -> str:
    """Get the direct URL to a YouTube video - this function must be run in an executor as youtube-dl is a blocking library

    Args:
        source_url (str): The source YouTube video URL
        ydl_opts (dict[str], optional): options passed to youtube-dl. Defaults to {"quiet": True}.

    Returns:
        str: the direct URL to the YouTube video - this is passed to aiohttp
    """
    with YoutubeDL(ydl_opts) as ydl:
        return ydl.extract_info(source_url, download=False)["formats"][-1]["url"]
