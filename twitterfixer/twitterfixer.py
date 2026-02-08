import discord
import re
import aiohttp
import json
import io
import os
from ffmpy import FFmpeg
from datetime import datetime
from redbot.core import commands
from redbot.core.bot import Red
from redbot.core.data_manager import cog_data_path


class TwitterFixer(commands.Cog, name='TwitterFixer'):
    def __init__(self, bot: Red):
        self.bot = bot

    async def redirect_to_vx(origin_message: discord.Message, new_message: discord.Message, tweet: dict):
        # when a re-encoded file or gif is too big for its intended server, send a vxtwitter link instead
        # delete the new embed and send a raw vxtwitter link instead
        link = tweet['tweetURL'].replace('twitter.com', 'vxtwitter.com')
        await new_message.delete()
        await origin_message.channel.send(link)

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

        content = message.content
        match = re.search(r'https://(?:twitter|x)\.com/(?:.*)/status/([0-9]*)', content)
        if match is None:
            return

        tweet_id = match.group()
        request_string = f'https://api.vxtwitter.com/status/{tweet_id}'
        async with aiohttp.ClientSession() as session:
            async with session.get(request_string) as response:
                if response.ok is True:
                    final_text = await response.text()
                    tweet = json.loads(final_text)

                    embed = discord.Embed(title=f"{tweet['user_name']} (@{tweet['user_screen_name']})", url=tweet['tweetURL'], description=tweet['text'], timestamp=datetime.fromtimestamp(tweet['date_epoch']))
                    embed.set_thumbnail(url=tweet['user_profile_image_url'])
                    embed.set_author(name="Twitter", url=f"https://twitter.com/{tweet['user_screen_name']}")
                    embed.add_field(name="Likes", value=tweet['likes'], inline=True)
                    embed.add_field(name="Retweets", value=tweet['retweets'], inline=True)
                    embed.add_field(name="Replies", value=tweet['replies'], inline=True)
                    embed.color = 0x26a7de

                    image_urls = []
                    gif_urls = []
                    video_urls = []

                    if len(tweet['mediaURLs']):
                        for media in tweet['media_extended']:
                            if media['type'] == 'image':
                                image_urls.append(media['url'])
                            elif media['type'] == 'gif':
                                gif_urls.append(media['url'])
                            elif media['type'] == 'video':
                                video_urls.append(media['url'])

                    if len(image_urls) > 1:
                        embed.set_image(url=f'https://convert.vxtwitter.com/rendercombined.jpg?imgs={",".join(image_urls)}')
                    elif len(image_urls) == 1:
                        embed.set_image(url=image_urls[0])

                    new_message = await message.channel.send(embed=embed)

                    # edit the original message to suppress any embed from twitter proper
                    await message.edit(suppress=True)

                    cog_path = cog_data_path(self)
                    for gif_url in gif_urls:
                        if os.path.exists(cog_path / 'original_video.mp4'):
                            os.remove(cog_path / 'original_video.mp4')

                        if os.path.exists(cog_path / 'gif.gif'):
                            os.remove(cog_path / 'gif.gif')

                        async with aiohttp.ClientSession() as session:
                            async with session.get(gif_url) as response:
                                with open(cog_path / 'original_video.mp4', 'wb') as file:
                                    temp = await response.read()
                                    data = io.BytesIO(temp)
                                    file.write(data.getbuffer())

                                async with message.channel.typing():
                                    ff = FFmpeg(
                                        inputs={cog_path / 'original_video.mp4': None},
                                        outputs={cog_path / 'gif.gif': '-filter_complex "[0:v] split [a][b];[a] palettegen [p];[b][p] paletteuse"'}
                                    )
                                    ff.run()

                                if os.path.getsize(cog_path / 'gif.gif') > message.guild.filesize_limit:
                                    await self.redirect_to_vx(message, new_message, tweet)
                                else:
                                    discord_attachment = discord.File(cog_path / 'gif.gif')
                                    await message.channel.send(file=discord_attachment)

                                os.remove(cog_path / 'original_video.mp4')
                                os.remove(cog_path / 'gif.gif')

                    for video_url in video_urls:
                        async with aiohttp.ClientSession() as session:
                            async with message.channel.typing():
                                async with session.get(video_url) as response:
                                    temp = await response.read()
                                    if len(temp) > message.guild.filesize_limit:
                                        await self.redirect_to_vx(message, new_message, tweet)
                                        break
                                    with io.BytesIO(temp) as file:
                                        newfile = discord.File(file, 'video.mp4')
                                        await message.channel.send(file=newfile)
