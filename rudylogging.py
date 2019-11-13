import discord
import asyncio
from discord.ext import commands
from utility import rcrp_utility

class LoggingCog(commands.Cog, name="Logging"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if message.author.id == 311318305564655637: #mussy's id
            em=discord.Embed(title='Message Deleted', description="Mussy deleted a message like a bitch. Let's see what it was!", color = 0xe74c3c, timestamp = message.created_at)
            em.add_field(name='Message Content', value=message.content, inline=False)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            em.set_footer(text=f"User ID: {message.author.id}")
            await message.channel.send(embed=em)

        if rcrp_utility.isstaffchannel(before.channel.id) == False and before.guild is not None:
            deletechan = self.bot.get_channel(rcrp_utility.deletelogchannel())
            em=discord.Embed(title='Message Deleted', description=f'Message by {message.author.mention} in {message.channel.mention} was deleted', color = 0xe74c3c, timestamp = message.created_at)
            em.add_field(name='Message Content', value=message.content, inline=False)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            em.set_footer(text=f"User ID: {message.author.id}")
            await deletechan.send(embed=em)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if rcrp_utility.isstaffchannel(before.channel.id) == False and before.guild is not None:
            if before.content == after.content:
                return

            editchan = self.bot.get_channel(rcrp_utility.editlogchannel())
            em=discord.Embed(title='Message Edited', description=f'{before.author.mention} edited a message in {before.channel.mention}', color = 0xe74c3c, timestamp = after.edited_at)
            em.add_field(name='Original Message', value=before.content, inline=False)
            em.add_field(name='New Message', value=after.content, inline=False)
            em.set_author(name=after.author, icon_url=after.author.avatar_url)
            em.set_footer(text=f"User ID: {after.author.id}")
            await editchan.send(embed=em)

def setup(bot):
    bot.add_cog(LoggingCog(bot))