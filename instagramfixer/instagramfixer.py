import discord
from redbot.core import commands
from redbot.core.bot import Red


class InstagramFixer(commands.Cog, name='InstagramFixer'):
    def __init__(self, bot: Red):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild is None:
            return

        if message.author.bot is True:
            return

        if message.author.guild_permissions.embed_links is False:
            return

        bot_member = message.guild.get_member(self.bot.user.id)
        if bot_member.guild_permissions.manage_messages is False:
            return

        if message.content.find('https://www.instagram.com/') == -1:
            return

        fixed_link = message.content.replace('https://www.instagram.com/', 'https://www.ddinstagram.com/')
        await message.channel.send(fixed_link)

        # edit the original message to suppress any embed from instagram proper
        await message.edit(suppress=True)
