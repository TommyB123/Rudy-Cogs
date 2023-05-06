import discord
import random
from imgurpython import ImgurClient
from typing import Union
from redbot.core import commands, app_commands, Config
from redbot.core.bot import Red

# imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')


async def isrudyfriend(ctx: commands.Context):
    rudy = RudyPic(commands.Cog)
    rudy.config = Config.get_conf(rudy, identifier=45599)
    async with rudy.config.rudy_friends() as friends:
        if ctx.author.id in friends:
            return True

    async with rudy.config.rudy_guilds() as guilds:
        if ctx.guild is not None and ctx.guild.id in guilds:
            return True

    async with rudy.config.rudy_channels() as channels:
        if ctx.channel is not None and ctx.channel.id in channels:
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

    async def send_album_picture(self, context: Union[commands.Context, discord.Interaction], album: str):
        final_url = None
        try:
            async with context.typing():
                pictures = []
                for image in imclient.get_album_images(album):
                    pictures.append(image.link)
                final_url = random.choice(pictures)
        except Exception:
            pass

        if isinstance(context, commands.Context):
            await context.send(final_url)
        elif isinstance(context, discord.Interaction):
            await context.response.send_message(final_url)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.check(isrudyfriend)
    @app_commands.choices(pictype=[
        app_commands.Choice(name='Rudy', value='WLQku0l'),
        app_commands.Choice(name='Sammy', value='VfKwj4H'),
        app_commands.Choice(name='Milo', value='h3VORpQ'),
        app_commands.Choice(name='Annie', value='MkkXNpx'),
        app_commands.Choice(name='gizmo', value='SlgjJJu'),
        app_commands.Choice(name='lylat', value='LF00KOm')
    ])
    async def pic(self, interaction: discord.Interaction, pictype: str):
        await self.send_album_picture(interaction, pictype)

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
