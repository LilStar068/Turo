from bot import TuroBot
from config import Config


def main():
    bot = TuroBot(config=Config())
    bot.run()


if __name__ == "__main__":
    main()
