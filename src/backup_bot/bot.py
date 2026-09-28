import enum
import logging
import os

import aiofiles
import discord
import dotenv
from discord import app_commands
from discord.ext import commands, tasks
from discord.ext.commands.context import Context

logger = logging.getLogger("discord")
logger.setLevel(logging.INFO)

"""
    Command Groups
"""
backup_group = app_commands.Group(
    name="backup", description="Backup text channel or thread!"
)

"""
    Bot specific classses
"""


class FormatOption(enum.Enum):
    Text = "txt"
    Markdown = "md"


class BackupBot(commands.Bot):
    def __init__(self):
        self.output_dir = "output"
        intents = discord.Intents.default()
        intents.message_content = True

        if not os.path.isdir(self.output_dir):
            os.mkdir(self.output_dir)

        super().__init__(command_prefix="$", intents=intents)

    async def setup_hook(self) -> None:
        self.tree.add_command(backup_group)
        await self.tree.sync()
        logger.info("Commands synced globally.")

        await self.cleanup_output_dir()

        return await super().setup_hook()

    async def write_to_file(
        self,
        messages: list[discord.Message],
        format: FormatOption,
        include_usernames: bool | None,
    ) -> discord.File:
        match format:
            case FormatOption.Text:
                extension = ".txt"
            case FormatOption.Markdown:
                extension = ".md"

        output_file = f"{self.output_dir}/{extension}"

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

    def get_id_from_link(self, link: str) -> tuple[int | None, int | None]:
        # https://discord.com/channels/891483017900613652/1486944125067460722
        if not link.startswith("https://discord.com/channels/"):
            return (None, None)

        link_parts = link.split("/")
        if not link_parts:
            return (None, None)

        # returns channel_id, guild_id as ints
        return (int(link_parts[-1]), int(link_parts[-2]))

    @tasks.loop(minutes=60)
    async def cleanup_output_dir(self):
        outfiles = [
            os.path.join(self.output_dir, file)
            for file in os.listdir(self.output_dir)
            if os.path.isfile(os.path.join(self.output_dir, file))
        ]
        for file in outfiles:
            os.remove(file)
        logger.info(f"Cleaned up output dir: {self.output_dir}")

    @cleanup_output_dir.before_loop
    async def before_cleanup(self):
        await self.wait_until_ready()


bot = BackupBot()

"""
    Events and commands
"""


@bot.event
async def on_ready() -> None:
    assert bot.user is not None
    logger.info(f"Logged in as: {bot.user} (ID: {bot.user.id})")
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
        f"{interaction.user.mention} Here's the thread backup you requested!",
        file=backup_file,
    )


"""
    This whole command feels ugly.  Idk.
    Maybe I'm overthinking it, but I should come back to rewrite this at some point, probably.
    TODO: this. lol. sorry future me.
"""
@backup_group.command(name="link", description="Backup a thread/channel from a link!")
async def backup_link(
    interaction: discord.Interaction,
    link: str,
    format: FormatOption,
    include_usernames: bool | None,
):
    await interaction.response.defer()
    if not interaction.guild:
        await interaction.followup.send(
            "Sorry, this command should be run from within a guild.", ephemeral=True
        )
        return

    channel_id, guild_id = bot.get_id_from_link(link)
    if not channel_id or not guild_id:
        await interaction.followup.send(
            "Something went wrong! Please verify that your link was correct."
        )
        return

    channel = await bot.fetch_channel(channel_id)  # pyright: ignore[reportArgumentType] - Already checked for None case above.
    if not isinstance(channel, discord.TextChannel or discord.Thread):
        await interaction.followup.send(
            "Was that a Text channel or a thread you sent? If so I failed to parse it.  Rip.",
            ephemeral=True,
        )
        return

    backup_file = await bot.backup(channel, format, include_usernames)
    await interaction.followup.send(
        f"{interaction.user.mention} Here's the backup you requested!", file=backup_file
    )


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


def start_bot():
    dotenv.load_dotenv()
    token = os.environ.get("DISCORD_BOT_TOKEN")
    assert token is not None

    bot.run(token)
