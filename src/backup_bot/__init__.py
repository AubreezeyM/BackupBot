import logging

from backup_bot import bot

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

def main() -> None:
    bot.start_bot()
