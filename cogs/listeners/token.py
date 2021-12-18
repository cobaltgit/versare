import discord
import json
import re
from discord.ext import commands


class TokenInvalidator(commands.Cog):
    """Checks for tokens in messages and invalidates them"""
    def __init__(self, bot):
        self.bot = bot
        self.TOKEN_REGEX = re.compile(r"([a-zA-Z0-9]{24}\.[a-zA-Z0-9]{6}\.[a-zA-Z0-9_\-]{27}|mfa\.[a-zA-Z0-9_\-]{84})")
        self.API_ENDPOINT = "https://api.github.com/gists"

    @commands.Cog.listener()
    async def on_message(self, message):
        tokens = re.findall(self.TOKEN_REGEX, message.content)
        if tokens:
            await message.delete()
            data = {
                "description": "Versare Automated Token Invalidation",
                "public": True,
                "files": {
                    "invalidated-token": {
                        "content": "\n".join(tokens)
                    }
                }
            }
            params = {'scope':'gist'}
            headers = {'Authorization':f'token {self.bot.auth.get("github_token")}'}
            async with self.bot.httpsession.post(self.API_ENDPOINT, params=params, data=json.dumps(data), headers=headers) as r:
                r = await r.json()
            return await message.channel.send(f"Found {len(tokens)} token(s) in message - invalidated\n{r['html_url']}")
    

def setup(bot):
    if bot.auth.get("github_token"):
        bot.add_cog(TokenInvalidator(bot))
