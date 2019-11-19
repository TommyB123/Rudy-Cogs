import discord
import asyncio
from discord.ext import commands

#discord bot handler
client = commands.Bot(command_prefix='!')

cogs = [
    'cogs.commands_fun',
    'cogs.commands_player',
    'cogs.commands_staff',
    'cogs.commands_owner',
    'cogs.commands_weeb',
    'cogs.rudylogging',
    'cogs.messagequeue',
    'cogs.rolesync',
    'cogs.rudypic',
    'cogs.sampinfo',
    'cogs.verification'
]

@client.event
async def on_ready():
    print(f'\nLogged in as {client.user.name}')
    print(client.user.id)

    if __name__ == '__main__':
        for cog in cogs:
            try: 
                client.load_extension(cog)
            except Exception as e:
                print(f'Failed load {cog}. Reason: {e}')
            else:
                print(f'Cog {cog} successfully loaded.')
    print('------')

@client.event
async def on_message(message):
    if client.user.id == message.author.id:
        return

    await client.process_commands(message)

@client.event
async def on_command_error(context, exception):
    exceptionchannel = client.get_channel(644115120154345472)
    await exceptionchannel.send(f'A command exception was caught: {exception}')

client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0")