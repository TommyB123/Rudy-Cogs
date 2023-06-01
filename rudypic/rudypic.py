import discord
import json
import random
import requests
from typing import Union
from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red


async def isrudyfriend(interaction: discord.Interaction):
    rudy = RudyPic(commands.Cog)
    rudy.config = Config.get_conf(rudy, identifier=45599)
    async with rudy.config.rudy_friends() as friends:
        if interaction.user is not None and interaction.user.id in friends:
            return True

    async with rudy.config.rudy_guilds() as guilds:
        if interaction.guild is not None and interaction.guild.id in guilds:
            return True

    async with rudy.config.rudy_channels() as channels:
        if interaction.channel is not None and interaction.channel.id in channels:
            return True

    return False


class RudyPic(commands.Cog, name="rudypic"):
    def __init__(self, bot: Red):
        self.bot = bot
        default_global = {
            "rudy_friends": [],
            "rudy_guilds": [],
            "rudy_channels": []
        }

        self.config = Config.get_conf(self, identifier=45599)
        self.config.register_global(**default_global)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.check(isrudyfriend)
    @app_commands.choices(animal=[
        app_commands.Choice(name='Rudy', value='WLQku0l'),
        app_commands.Choice(name='Sammy', value='VfKwj4H'),
        app_commands.Choice(name='Milo', value='h3VORpQ'),
        app_commands.Choice(name='Annie', value='MkkXNpx'),
        app_commands.Choice(name='gizmo', value='SlgjJJu'),
        app_commands.Choice(name='lylat', value='LF00KOm')
    ])
    async def pic(self, interaction: discord.Interaction, animal: str):
        """Sends a photograph of an esteemed animal + some other silly shit"""
        url = f'https://api.imgur.com/3/album/{animal}/images'
        headers = {'Authorization': 'Client-ID 6f85cfd1f822e7b'}
        response = requests.request("GET", url, headers=headers)
        data = json.loads(response.text)
        image = random.choice(data['data'])
        await interaction.response.send_message(image['link'])

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def rudyfriend(self, ctx: commands.Context, target: Union[discord.Member, discord.TextChannel] = None):
        if isinstance(target, discord.Member):
            async with self.config.rudy_friends() as rudyfriends:
                if target.id in rudyfriends:
                    rudyfriends.remove(target.id)
                    await ctx.send(f'{target.mention} is no longer a Rudy friend!')
                else:
                    rudyfriends.append(target.id)
                    await ctx.send(f'{target.mention} is now a Rudy friend!')
        elif isinstance(target, discord.TextChannel):
            async with self.config.rudy_channels() as rudychannels:
                if target.id in rudychannels:
                    rudychannels.remove(target.id)
                    await ctx.send(f'{target.mention} is no longer a Rudy friend channel!')
                else:
                    rudychannels.append(target.id)
                    await ctx.send(f'{target.mention} is now a Rudy friend channel!')
        elif target is None and ctx.guild is not None:
            async with self.config.rudy_guilds() as rudyguilds:
                if ctx.guild.id in rudyguilds:
                    rudyguilds.remove(ctx.guild.id)
                    await ctx.send(f'{ctx.guild.name} is no longer a Rudy friend guild!')
                else:
                    rudyguilds.append(ctx.guild.id)
                    await ctx.send(f'{ctx.guild.name} is now a Rudy friend guild!')
