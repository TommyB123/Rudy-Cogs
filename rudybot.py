import discord
import asyncio
from discord.ext import commands
from config import bot_token

#discord bot handler
client = commands.Bot(command_prefix='!')

cogs = [
    'commands_fun',
    'commands_help',
    'commands_owner',
    'commands_player',
    'commands_staff',
    'commands_weeb',
    'messagequeue',
    'rolesync',
    'rudylogging',
    'rudypic',
    'sampinfo',
    'verification'
]

@client.event
async def on_ready():
    print(f'\nLogged in as {client.user.name}')
    print(client.user.id)

    if __name__ == '__main__':
        for cog in cogs:
            if client.get_cog(cog) == None:
                try:
                    client.load_extension(f'cogs.{cog}')
                except Exception as e:
                    print(f'Failed load {cog}. Reason: {e}')
                else:
                    print(f'Cog {cog} successfully loaded.')
            else:
                print(f'Cog {cog} is already loaded.')
    print('All cogs successfully loaded. Bot is ready 2 go')

@client.event
async def on_message(message):
    if client.user.id == message.author.id:
        return

    await client.process_commands(message)

@client.event
async def on_command_error(context, exception):
    exceptionchannel = client.get_channel(644115120154345472)
    await exceptionchannel.send(f'A command exception was caught: {exception}')

client.run(bot_token)