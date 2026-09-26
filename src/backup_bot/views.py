import discord
import aiofiles
from discord.threads import Thread

async def backup_thread(channel: Thread | discord.TextChannel) -> str:
    out_file = 'output.txt'
    async with aiofiles.open(out_file, 'w') as file:
        async for message in channel.history(oldest_first=True, limit=None):
            await file.write(f'{message.author}: {message.content}\n')


    return out_file
"""
class ChannelMenu(discord.ui.Select):
    def __init__(self, channels: list[discord.TextChannel]):
        options= [
            discord.SelectOption(label=f'{channel}') for channel in channels
        ]
        super().__init__(placeholder='Choose the channel to backup', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message('This ain\'t a guild or something! Figure that out first.')
            return

        selected_channel = self.values[0]
        channels = get_channels(guild)

        for channel in channels:
            if channel.name == selected_channel:
                await interaction.response.defer()
                outfile = await backup_thread(channel)
                await interaction.followup.send('Here\'s your backup, my lord!', file=discord.File(outfile))


class ChannelMenuView(discord.ui.View):
    def __init__(self, channels: list[discord.TextChannel]):
        super().__init__()
        self.add_item(ChannelMenu(channels))

class ThreadMenu(discord.ui.Select):
    def __init__(self, threads: list[Thread]):
        options= [
            discord.SelectOption(label=f'{thread}') for thread in threads
        ]
        super().__init__(placeholder='Choose the thread to backup', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message('This ain\'t a guild or something! Figure that out first.')
            return

        selected_thread = self.values[0]
        threads = get_threads(guild)

        for thread in threads:
            if thread.name == selected_thread:
                await interaction.response.defer()
                outfile = await backup_thread(thread)
                await interaction.followup.send('Here\'s your backup, my lord!', file=discord.File(outfile))


class ThreadMenuView(discord.ui.View):
    def __init__(self, threads: list[Thread]):
        super().__init__()
        self.add_item(ThreadMenu(threads))

class ThreadOrChannelSelectLayout(discord.ui.LayoutView):
    action_row = discord.ui.ActionRow()

    @action_row.button(label='Thread')
    async def thread_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        if guild is None:
            await interaction.response.send_message('This ain\'t a guild or something! Figure that out first.')
            return

        threads = get_threads(guild)
        await interaction.response.send_message(view=ThreadMenuView(threads))

    @action_row.button(label='Channel')
    async def channel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        assert interaction.guild is not None
        channels = get_channels(interaction.guild)

        await interaction.response.send_message(view=ChannelMenuView(channels))
"""