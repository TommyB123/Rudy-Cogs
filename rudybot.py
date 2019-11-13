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

@client.event
async def on_command_error(context, exception):
    exceptionchannel = client.get_channel(644115120154345472)
    await exceptionchannel.send(f'A command exception was caught: {exception}')

@client.command(hidden = True)
@commands.is_owner()
async def loadcog(ctx, *, cog:str):
    try:
        client.load_extension(cog)
    except Exception as e:
        await ctx.send(f'Unable to load {cog}. Reason: {e}')
    else:
        await ctx.send(f'{cog} loaded successfully.')

@client.command(hidden = True)
@commands.is_owner()
async def unloadcog(ctx, *, cog:str):
    try:
        client.unload_extension(cog)
    except Exception as e:
        await ctx.send(f'Unable to unload {cog}. Reason: {e}')
    else:
        await ctx.send(f'{cog} unloaded successfully.')

@client.command(hidden = True)
@commands.is_owner()
async def reloadcog(ctx, *, cog:str):
    try:
        client.unload_extension(cog)
        client.load_extension(cog)
    except Exception as e:
        await ctx.send(f'Relaoding of {cog} failed. Reason: {e}')
    else:
        await ctx.send(f'{cog} successfully reloaded.')

client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0")