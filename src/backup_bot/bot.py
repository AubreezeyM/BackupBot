import enum
import logging
import os

import aiofiles
from backup_bot.context_menus.backup import backup_from_menu, backup_to_menu
import discord
import dotenv
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands.context import Context

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

class BackupBot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(command_prefix="$", intents=intents)

    async def setup_hook(self) -> None:
        self.tree.add_command(backup_from_menu)
        self.tree.add_command(backup_to_menu)
        await self.tree.sync()
        logger.info("Cogs loaded and commands synced globally.")

        return await super().setup_hook()

    async def check_if_owner(self, ctx: Context) -> bool:
        owner_id = os.environ.get("OWNER_USER_ID")
        if not owner_id:
            print(
                "!! Unable to use command as no owner ID was found in Environment! !!"
            )
            return False

        if ctx.author.id != int(owner_id):
            await ctx.send(
                "Sorry, you need to be the bot owner to use this command.  If it's you, check the bots logs!"
            )
            return False

        return True

bot = BackupBot()

@bot.event
async def on_ready() -> None:
    assert bot.user is not None
    logger.info(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    print("------------")


@bot.command(name="printcommands")
async def printcommands(ctx: Context):
    if await bot.check_if_owner(ctx):
        commands_list = bot.tree.get_commands()
        for command in commands_list:
            if isinstance(command, app_commands.Group):
                for com in command.commands:
                    print(f"{command.name}: {com.name}")
            else:
                print(command.name)

# TODO: Maybe move this into __init__.py? Idk.
def start_bot():
    dotenv.load_dotenv()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    assert token is not None

    bot.run(token)
