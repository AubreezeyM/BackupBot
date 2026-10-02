import json

import discord
import aiofiles
from discord import app_commands
import enum

OUTPUT_DIR = 'output/'

async def write_to_file(
    messages: list[discord.Message],
) -> discord.File:

    output_file = f"{OUTPUT_DIR}/backup.json"
    final_list: list[dict[str, str]] = []

    for message in messages:
        obj = {}
        obj["message_id"] = str(message.id)
        obj["author"] = message.author.name
        obj["content"] = message.content

        final_list.append(obj)

    async with aiofiles.open(output_file, "w") as file:
        await file.write(json.dumps(final_list))

    return discord.File(output_file)

async def backup_from(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    messages = [message] + [msg async for msg in message.channel.history(
        oldest_first=True,
        limit=None,
        after=message
    )]

    backup_file = await write_to_file(messages)
    await interaction.followup.send(f'{message.author.mention} Here\'s your backup!', file=backup_file, ephemeral=True)

backup_from_menu = app_commands.ContextMenu(
    name='Backup everything from here',
    callback=backup_from,
)

async def backup_to(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True)
    messages = [message] + [msg async for msg in message.channel.history(
        oldest_first=True,
        limit=None,
        before=message
    )]

    backup_file = await write_to_file(messages)
    await interaction.followup.send(f'{message.author.mention} Here\'s your backup!', file=backup_file, ephemeral=True)

backup_to_menu = app_commands.ContextMenu(
    name='Backup everything to here',
    callback=backup_to,
)
