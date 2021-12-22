from bot import Versare

if __name__ == "__main__":
    if __import__("os").name != "nt":
        try:
            import uvloop
        except ImportError:
            pass
        else:
            uvloop.install()

    bot = Versare()
    bot.run(bot.config.get("auth", {}).get("token"))
