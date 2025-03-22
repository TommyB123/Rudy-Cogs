import discord
import os
from ffmpy import FFmpeg
from redbot.core.bot import Red
from redbot.core import commands, Config
from redbot.core.data_manager import cog_data_path


class WebMFixer(commands.Cog, name='WebM Fixer'):
    def __init__(self, bot: Red):
        self.bot = bot

        default_guild = {
            "enabled": False
        }

        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if self.config.guild(message.guild).enabled.get() is False:
            return

        if len(message.attachments):
            cog_path = cog_data_path(self)
            for attachment in message.attachments:
                if attachment.filename.endswith('.webm'):
                    await attachment.save(cog_path / attachment.filename)
                    newname = attachment.filename.removesuffix('webm')
                    newname += 'mp4'

                    async with message.channel.typing():
                        ff = FFmpeg(
                            inputs={cog_path / attachment.filename: None},
                            outputs={cog_path / newname: None}
                        )
                        ff.run()

                        new_attachment = discord.File(cog_path / newname)
                        poster_name = message.author.name if message.author.nick is None else message.author.nick
                        await message.channel.send(f'{poster_name}\'s video but not as a WebM', file=new_attachment)

                        os.remove(cog_path / attachment.filename)
                        os.remove(cog_path / newname)

    @commands.command()
    @commands.guild_only()
    @commands.admin_or_permissions(manage_guild=True)
    async def webmfixer(self, ctx: commands.Context):
        """Toggle bot re-encoding of WebM videos to regular mp4s"""
        fixer_state = await self.config.guild(ctx.guild).enabled.get()
        if fixer_state is True:
            await self.config.guild(ctx.guild).enabled.set(False)
            await ctx.send('You have disabled WebM re-encoding.')
        else:
            await self.config.guild(ctx.guild).enabled.set(True)
            await ctx.send('You have enabled WebM re-encoding')
