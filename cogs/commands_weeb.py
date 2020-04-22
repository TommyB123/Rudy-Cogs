import discord
import aiohttp
import json
from discord.ext import commands

#tommy, graber, cave & amir
weebs = [87582156741681152, 253685655471783936, 273956905397911553, 413452980470415361]

async def isweeb(ctx):
	if ctx.author.id in weebs:
		return True
	else:
		return False

async def fetchweeb(session, url):
	async with session.get(url) as response:
		return await response.text()

class WeebCog(commands.Cog, name = "Weeb"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command(help = "Bad")
	@commands.guild_only()
	@commands.check(isweeb)
	async def weeb(self, ctx):
		async with aiohttp.ClientSession() as session:
			response = await fetchweeb(session, 'https://nekos.life/api/v2/img/neko')
			image = json.loads(response)
			await ctx.send(image['url'])

	@commands.command(help = "Bad (old)")
	@commands.guild_only()
	@commands.check(isweeb)
	@commands.cooldown(1, 60)
	async def oldweeb(self, ctx):
		async with aiohttp.ClientSession() as session:
			response = await fetchweeb(session, 'https://neko-love.xyz/api/v1/neko')
			image = json.loads(response)
			await ctx.send(image['url'])

	@commands.command(help = "Really bad")
	@commands.guild_only()
	@commands.is_nsfw()
	@commands.check(isweeb)
	async def lewdweeb(self, ctx):
		async with aiohttp.ClientSession() as session:
			response = await fetchweeb(session, 'https://neko-love.xyz/api/v1/nekolewd')
			image = json.loads(response)
			await ctx.send(image['url'])

def setup(bot):
	bot.add_cog(WeebCog(bot))