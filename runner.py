from client import Versare

if __name__ == "__main__":
    if __import__("os").name != "nt":
        try:
            import uvloop
        except (ImportError, ModuleNotFoundError):
            pass
        else:
            uvloop.install()

    bot = Versare()
    bot.run(bot.token)
