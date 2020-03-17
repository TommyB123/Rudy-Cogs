import discord
from discord.ext import commands

#message delete log channel
deletelogs = 463595960367579137

#message edit log channel
editlogs = 463644249108250635

#channels where deletions/edits are not logged
staffchannels = [412340704187252748, 388002249013460993, 463595960367579137, 463644249108250635, 406166047167741952, 464899293166305291, 445668156824879123, 466946121445539840, 507547199710822400, 639337212424617994]

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

        if message.channel.id not in staffchannels and message.guild is not None:
            deletechan = self.bot.get_channel(deletelogs)
            em=discord.Embed(title='Message Deleted', description=f'Message by {message.author.mention} in {message.channel.mention} was deleted', color = 0xe74c3c, timestamp = message.created_at)
            em.add_field(name='Message Content', value=message.content, inline=False)
            em.set_author(name=message.author, icon_url=message.author.avatar_url)
            em.set_footer(text=f"User ID: {message.author.id}")
            await deletechan.send(embed=em)

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.channel.id not in staffchannels and before.guild is not None:
            if before.content == after.content:
                return

            editchan = self.bot.get_channel(editlogs)
            em=discord.Embed(title='Message Edited', description=f'{before.author.mention} edited a message in {before.channel.mention}', color = 0xe74c3c, timestamp = after.edited_at)
            em.add_field(name='Original Message', value=before.content, inline=False)
            em.add_field(name='New Message', value=after.content, inline=False)
            em.set_author(name=after.author, icon_url=after.author.avatar_url)
            em.set_footer(text=f"User ID: {after.author.id}")
            await editchan.send(embed=em)

def setup(bot):
    bot.add_cog(LoggingCog(bot))