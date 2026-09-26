import enum
import os

import aiofiles
import discord
import dotenv
from discord import app_commands
from discord.ext import commands
from discord.ext.commands.context import Context

class FormatOption(enum.Enum):
    Text = "txt"
    Markdown = "md"
    # JSON = 'json' ### was a good idea in theory, couldn't find a use case in practice.  Keeping it just because.


class BackupBot(commands.Bot):
    def __init__(self):
        self.output_dir = "output"
        intents = discord.Intents.default()
        intents.message_content = True

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        super().__init__(command_prefix="$", intents=intents)

    async def write_to_file(
        self,
        messages: list[discord.Message],
        format: FormatOption,
        include_usernames: bool | None,
    ) -> discord.File:
        output_file = f"{self.output_dir}/output"
        match format:
            case FormatOption.Text:
                output_file = output_file + ".txt"
            case FormatOption.Markdown:
                output_file = output_file + ".md"

        async with aiofiles.open(output_file, "w") as file:
            if include_usernames:
                for message in messages:
                    await file.write(f"{message.author}: {message.content}\n\n")
            else:
                for message in messages:
                    await file.write(f"{message.content}\n\n")

        return discord.File(output_file)

    async def backup(
        self,
        channel: discord.TextChannel | discord.Thread,
        format: FormatOption,
        include_usernames: bool | None,
    ) -> discord.File:
        messages = [
            message async for message in channel.history(oldest_first=True, limit=None)
        ]
        return await self.write_to_file(messages, format, include_usernames)


bot = BackupBot()
backup_group = app_commands.Group(
    name="backup", description="Backup text channel or thread!"
)

@bot.event
async def on_ready() -> None:
    assert bot.user is not None
    bot.tree.add_command(backup_group)

    print(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    print("------------")


@backup_group.command(name="channel", description="Backup a text thread.")
async def backup_thread(
    interaction: discord.Interaction,
    channel: discord.Thread | discord.TextChannel,
    format: FormatOption,
    include_usernames: bool | None,
) -> None:
    await interaction.response.defer()
    await interaction.followup.send(
        f"Preparing the requested backup for **{channel.name}**.  This may take a minute for longer threads, so hang tight!"
    )

    backup_file = await bot.backup(channel, format, include_usernames)
    await interaction.followup.send(
        f"@{interaction.user.mention} Here's the thread backup you requested!", file=backup_file
    )


async def check_if_owner(ctx: Context) -> bool:
    owner_id = os.environ.get("OWNER_USER_ID")
    if not owner_id:
        print("!! Unable to use command as no owner ID was found in Environment! !!")
        return False

    if ctx.author.id != int(owner_id):
        await ctx.send('Sorry, you need to be the bot owner to use this command.  If it\'s you, check the bots logs!')
        return False

    return True

@bot.command(name="syncslash")
async def sync(ctx: Context):
    if await check_if_owner(ctx):
        print("Syncing commands globally...")
        bot.tree.add_command(backup_group)
        await bot.tree.sync()
        await ctx.send("Commands synced globally.")
        return

def start_bot():
    dotenv.load_dotenv()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    assert token is not None

    bot.run(token)
