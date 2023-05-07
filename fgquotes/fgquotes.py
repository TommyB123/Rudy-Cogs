import discord
from redbot.core.bot import Red
import random
from redbot.core import commands, app_commands, Config

# FG guild id
fgguildid = 93140261797904384


def fg_check(interaction: discord.Interaction):
    return interaction.guild is not None and interaction.guild.id == fgguildid


class FGQuotes(commands.Cog, name='FrostGaming Quotes'):
    def __init__(self, bot: Red):
        default_guild = {
            "quotes": []
        }

        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    @app_commands.command()
    @app_commands.guild_only()
    @app_commands.check(fg_check)
    async def quote(self, interaction: discord.Interaction):
        """Fetches a quote"""
        async with self.config.guild(interaction.guild).quotes() as quotes:
            quote = random.choice(quotes)
            await interaction.response.send_message(quote)

    quotemanage = app_commands.Group(name='quotemanage', description='Manipulate stored quotes')

    @quotemanage.command(name='add', description='Add a new quote to the list')
    @app_commands.describe(quote="The quote you'd like to add")
    async def quotemanage_add(self, interaction: discord.Interaction, *, quote: str):
        async with self.config.guild(interaction.guild).quotes() as quotes:
            if quote in quotes:
                await interaction.response.send_message('This quote is already in the quote list (lol)')
            else:
                quotes.append(quote)
                await interaction.response.send_message('Quote added.')

    @quotemanage.command(name='delete', description='Delete stored quotes')
    @app_commands.guild_only()
    @app_commands.check(fg_check)
    async def quotemanage_delete(self, interaction: discord.Interaction, *, quote: str):
        """Removes a quote from the quote list"""
        async with self.config.guild(interaction.guild).quotes() as quotes:
            if quote not in quotes:
                await interaction.response.send_message('This quote is not present in the quotes list.')
            else:
                quotes.remove(quote)
                await interaction.response.send_message('Quote removed.')
