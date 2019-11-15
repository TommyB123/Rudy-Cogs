import discord
import httpx
import json
from discord.ext import commands

weebs = [87582156741681152, 253685655471783936, 273956905397911553] #tommy, graber & cave
weebcategories = ['neko', 'kitsune', 'hug', 'pat', 'waifu', 'cry', 'kiss']

async def isweeb(ctx):
	if ctx.author.id in weebs:
		return True
	else:
		return False

class WeebCog(commands.Cog, name = "Weeb Commands"):
	def __init__(self, bot):
		self.bot = bot

	@commands.command()
	@commands.check(isweeb)
	@commands.cooldown(1, 60)
	async def weeb(self, ctx, category:str = ''):
		category = category.lower()
		if category not in weebcategories:
			await ctx.send('Invalid category. Valid categories: {0}.'.format(', '.join(weebcategories)))
			return

		async with httpx.AsyncClient() as client:
			response = await client.get(f'https://neko-love.xyz/api/v1/{category}')
			await ctx.send(response.json()['url'])

def setup(bot):
	bot.add_cog(WeebCog(bot))