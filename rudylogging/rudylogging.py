import discord
from redbot.core import commands, Config
from redbot.core.bot import Red


class RudyLogging(commands.Cog, name="Rudy Logging"):
    def __init__(self, bot: Red):
        self.bot = bot

        default_guild = {
            "deletelogchannel": None,
            "editlogchannel": None,
            "ignorechannels": []
        }

        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    @commands.Cog.listener()
    async def on_message_delete(self, message: discord.Message):
        deletechannelid: int = await self.config.guild(message.guild).deletelogchannel()
        if deletechannelid is None:
            return

        ignorechannels: list = await self.config.guild(message.guild).ignorechannels()
        if message.channel.id in ignorechannels:
            return

        deletechannel = self.bot.get_channel(deletechannelid)
        embed = discord.Embed(title='Message Deleted', color=message.author.color, timestamp=message.created_at)
        embed.description = f'Message by {message.author.mention} in {message.channel.mention} was deleted'
        embed.add_field(name='Message Content', value=message.content, inline=False)
        embed.set_author(name=message.author, icon_url=message.author.avatar_url)
        embed.set_footer(text=f"User ID: {message.author.id}")
        await deletechannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_message_edit(self, before: discord.Message, after: discord.Message):
        if before.content == after.content:
            return

        editchannelid: int = await self.config.guild(before.guild).editlogchannel()
        if editchannelid is None:
            return

        ignorechannels: list = await self.config.guild(before.guild).ignorechannels()
        if before.channel.id in ignorechannels:
            return

        editchannel = self.bot.get_channel(editchannelid)
        embed = discord.Embed(title='Message Edited', color=before.author.color, timestamp=after.edited_at)
        embed.add_field(name='Original Message', value=before.content, inline=False)
        embed.add_field(name='New Message', value=after.content, inline=False)
        embed.set_author(name=after.author, icon_url=after.author.avatar_url)
        embed.set_footer(text=f"User ID: {after.author.id}")
        await editchannel.send(embed=embed)

    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel: discord.abc.GuildChannel):
        deletechannelid: int = await self.config.guild(channel.guild).deletechannel()
        if channel.id == deletechannelid:
            await self.config.guild(channel.guild).deletechannel.set(None)

        editchannelid: int = await self.config.guild(channel.id).editchannel()
        if channel.id == editchannelid:
            await self.config.guild(channel.guild).editchannel.set(None)

        async with self.config.guild(channel.guild).ignorechannels() as ignorechannels:
            if channel.id in ignorechannels:
                ignorechannels.remove(channel.id)

    @commands.group()
    @commands.guild_only()
    @commands.guildowner()
    async def rudylogging(self, ctx: commands.Context):
        """Log various Discord events"""
        pass

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def setdelete(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the channel whhich deleted messages get logged to"""
        await self.config.guild(ctx.guild).deletelogchannel.set(channel.id)
        await ctx.send(f'Message deletions will now log to {channel.mention}.')

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def setedit(self, ctx: commands.Context, channel: discord.TextChannel):
        """Sets the channel which edited messages get logged to"""
        await self.config.guild(ctx.guild).editlogchannel.set(channel.id)
        await ctx.send(f'Message edits will now log to {channel.mention}.')

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def ignore(self, ctx: commands.Context, channel: discord.TextChannel):
        """Adds or removes a channel from a list of channels that are skipped when logging"""
        async with self.config.guild(ctx.guild).ignorechannels() as channels:
            if channel.id not in channels:  # add the channel ID to the list
                channels.append(channel.id)
                await ctx.send(f'{channel.mention} has been added to the ignore list.')
            else:
                channels.remove(channel.id)
                await ctx.send(f'{channel.mention} has been removed from the ignore list.')

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def info(self, ctx: commands.Context):
        """Displays information related to logging functionality on this current server"""
        deletechannelid: int = await self.config.guild(ctx.guild).deletelogchannel()
        editchannelid: int = await self.config.guild(ctx.guild).editlogchannel()
        deletechannel = self.bot.get_channel(deletechannelid)
        editchannel = self.bot.get_channel(editchannelid)

        embed = discord.Embed(title='Logging Information', color=0xe74c3c, timestamp=ctx.message.created_at)
        embed.add_field(name='Message Deletions', value=deletechannel.mention if deletechannel is not None else "Not Set", inline=False)
        embed.add_field(name='Message Edits', value=editchannel.mention if editchannel is not None else "Not Set", inline=False)

        async with self.config.guild(ctx.guild).ignorechannels() as ignorelist:
            if len(ignorelist) != 0:
                message = []
                for id in ignorelist:
                    channel = self.bot.get_channel(id)
                    message.append(channel.mention)
                message = '\n'.join(message)
                embed.add_field(name='Ignored Channels', value=message, inline=False)

        await ctx.send(embed=embed)

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def removedelete(self, ctx: commands.Context):
        """Removes message deletion logging"""
        channelid: int = await self.config.guild(ctx.guild).deletelogchannel()
        channel: discord.TextChannel = self.bot.get_channel(channelid)
        await self.config.guild(ctx.guild).deletelogchannel.set(None)
        await ctx.send(f'Message deletions will no longer log to {channel.mention}.')

    @rudylogging.command()
    @commands.guild_only()
    @commands.guildowner()
    async def removeedit(self, ctx: commands.Context):
        """Removes message deletion logging"""
        channelid: int = await self.config.guild(ctx.guild).editlogchannel()
        channel: discord.TextChannel = self.bot.get_channel(channelid)
        await self.config.guild(ctx.guild).editlogchannel.set(None)
        await ctx.send(f'Message edits will no longer log to {channel.mention}.')
