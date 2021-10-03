import os, time

try:
    import dotenv
except ImportError:
    pass
else:
    dotenv.load_dotenv("env")


class Config:
    def __init__(self):
        self.bot_token: str = os.environ["BOT_TOKEN"]
        self.log_webhook_token: str = os.environ["WEBHOOK_TOKEN"]
        self.log_webhook_id = os.environ["WEBHOOK_ID"]
        self.database_url = os.environ["DATABASE_URL"]

start_time = time.time()
