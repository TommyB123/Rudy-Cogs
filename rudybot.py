import discord
import asyncio
from discord.ext import commands

#discord bot handler
client = commands.Bot(command_prefix='!')

client.remove_command('help')

cogs = ['cogs.commands_fun', 'cogs.commands_player', 'cogs.commands_staff', 'cogs.commands_owner', 'cogs.rudylogging', 'cogs.messagequeue', 'cogs.rolesync', 'cogs.rudypic', 'cogs.sampinfo', 'cogs.verification']

if __name__ == '__main__':
    for cog in cogs:
        client.load_extension(cog)

@client.event
async def on_ready():
    print(f'\nLogged in as {client.user.name}')
    print(client.user.id)
    print('------')

@client.event
async def on_message(message):
    if client.user.id == message.author.id:
        return

    if message.guild is not None:
        await client.process_commands(message)
        return

client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0")