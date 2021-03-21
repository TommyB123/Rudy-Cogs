import discord
import random
from redbot.core import commands, Config

# FG guild id
fgguildid = 93140261797904384


async def fg_check(ctx: commands.Context):
    return ctx.guild.id == fgguildid


class FGQuotes(commands.Cog, name='FrostGaming Quotes'):
    def __init__(self, bot: discord.Client):
        default_guild = {
            "quotes": []
        }

        self.bot = bot
        self.config = Config.get_conf(self, 45599)
        self.config.register_guild(**default_guild)

    @commands.command()
    @commands.guild_only()
    @commands.check(fg_check)
    async def quote(self, ctx: commands.Context):
        """Fetches a quote"""
        quotes: list = await self.config.guild(ctx.guild).quotes()
        quote = random.choice(quotes)
        await ctx.send(quote)

    @commands.group()
    @commands.guild_only()
    @commands.check(fg_check)
    async def managequote(self, ctx: commands.Context):
        """Manages the quote list"""
        pass

    @managequote.command()
    @commands.guild_only()
    @commands.check(fg_check)
    async def add(self, ctx: commands.Context, *, quote: str):
        """Adds a quote to the quote list"""
        quotes: list = await self.config.guild(ctx.guild).quotes()
        if quote in quotes:
            await ctx.send('This quote is already in the quote list (lol)')
            return

        quotes.append(quote)
        await self.config.guild(ctx.guild).quotes.set(quotes)
        await ctx.send('Quote added.')

    @managequote.command()
    @commands.guild_only()
    @commands.check(fg_check)
    async def remove(self, ctx: commands.Context, *, quote: str):
        """Removes a quote from the quote list"""
        quotes: list = await self.config.guild(ctx.guild).quotes()
        if quote not in quotes:
            await ctx.send('This quote is not present in the quotes list.')
            return

        quotes.remove(quote)
        await self.config.guild(ctx.guild).quotes.set(quotes)
        await ctx.send('Quote removed.')
