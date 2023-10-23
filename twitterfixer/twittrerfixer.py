import discord
import re
import aiohttp
import json
import io
from datetime import datetime
from redbot.core import commands
from redbot.core.bot import Red


class TwitterFixer(commands.Cog, name='TwitterFixer'):
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

        content = message.content
        match = re.search(r'https://(?:twitter|x)\.com/(?:.*)/status/([0-9]*)', content)
        if match is None:
            return

        tweet_id = match.group()
        request_string = f'https://api.vxtwitter.com/Twitter/status/{tweet_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(request_string) as response:
                if response.ok is True:
                    final_text = await response.text()
                    tweet = json.loads(final_text)

                    embed = discord.Embed(title=f"{tweet['user_name']} (@{tweet['user_screen_name']})", url=tweet['tweetURL'], description=tweet['text'], timestamp=datetime.fromtimestamp(tweet['date_epoch']))
                    embed.set_author(name="Twitter", url=f"https://twitter.com/{tweet['user_screen_name']}")
                    embed.add_field(name="Likes", value=tweet['likes'], inline=True)
                    embed.add_field(name="Retweets", value=tweet['retweets'], inline=True)
                    embed.add_field(name="Replies", value=tweet['replies'], inline=True)
                    embed.color = 0x26a7de

                    video_url = ''
                    if len(tweet['mediaURLs']):
                        if tweet['media_extended'][0]['type'] == 'image':
                            embed.set_image(url=tweet['mediaURLs'][0])
                        elif tweet['media_extended'][0]['type'] == 'video':
                            video_url = tweet['media_extended'][0]['url']

                    await message.channel.send(embed=embed)

                    if len(video_url):
                        async with aiohttp.ClientSession() as session:
                            async with session.get(video_url) as response:
                                temp = await response.read()
                                with io.BytesIO(temp) as file:
                                    newfile = discord.File(file)
                                    await message.channel.send(file=newfile)
