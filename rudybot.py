import discord
import asyncio
from discord.ext import commands
from config import bot_token
from utility import rcrpguildid

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
    'verification',
    'factions'
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
    if isinstance(exception, commands.UserInputError):
        await context.send(f'Invalid command syntax. Use `!help {context.invoked_with}` to view the valid syntax.')
        return
    
    if isinstance(exception, commands.CheckFailure):
        if context.guild.id == rcrpguildid:
            await context.message.add_reaction('\U0001F6AB') #no entry sign
        return

    if isinstance(exception, commands.CommandNotFound):
        if context.guild.id == rcrpguildid:
            await context.message.add_reaction('\u2753') #question mark
        return

    if context.guild.id == rcrpguildid and isinstance(exception, commands.CommandOnCooldown):
        await context.message.add_reaction('\U0001F192') #cool
        await context.message.add_reaction('\u2B07') #down
        return
    
    exceptionchannel = client.get_channel(644115120154345472)
    await exceptionchannel.send(f'A command exception was caught: {exception}')

@client.command()
@commands.guild_only()
@commands.is_owner()
async def loadcog(ctx, *, cogname:str):
    try:
        client.load_extension(f'cogs.{cogname}')
    except Exception as e:
        await ctx.send(f'Unable to load {cogname}. Reason: {e}')
    else:
        await ctx.message.add_reaction('\N{OK HAND SIGN}')

@client.command()
@commands.guild_only()
@commands.is_owner()
async def unloadcog(ctx, *, cogname:str):
    try:
        client.unload_extension(f'cogs.{cogname}')
    except Exception as e:
        await ctx.send(f'Unable to unload {cogname}. Reason: {e}')
    else:
        await ctx.message.add_reaction('\N{OK HAND SIGN}')

@client.command()
@commands.guild_only()
@commands.is_owner()
async def reloadcog(ctx, *, cogname:str):
    try:
        client.reload_extension(f'cogs.{cogname}')
    except Exception as e:
        await ctx.send(f'Reloading of {cogname} failed. Reason: {e}')
    else:
        await ctx.message.add_reaction('\N{OK HAND SIGN}')

client.run(bot_token)