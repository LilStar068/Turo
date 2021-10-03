from botbase import Bot
from config import Config


class TuroBot(Bot):
    def __init__(self, *, config: Config):
        super().__init__(
            description="",
            config=config,
        )
