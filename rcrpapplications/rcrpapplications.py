import discord
import aiomysql
from aiomysql import Cursor
from discord.ext import tasks
from redbot.core import commands
from redbot.core.bot import Red

# rcrp guild id
rcrpguildid = 93142223473905664

# applications channel ID
appchannelid = 445668156824879123


class RCRPApplications(commands.Cog, name='RCRP Applications'):
    def __init__(self, bot: Red):
        self.bot = bot
        self.applications = {}
        self.check_pending_applications.start()

    def cog_unload(self):
        self.check_pending_applications.cancel()

    async def log(self, message: str):
        rcrpguild = self.bot.get_guild(rcrpguildid)
        logchannel = rcrpguild.get_channel(775767985586962462)
        await logchannel.send(message)

    @tasks.loop(seconds=5.0)
    async def check_pending_applications(self):
        try:
            rcrpguild = await self.bot.fetch_guild(rcrpguildid)
            appchannel: discord.TextChannel = self.bot.get_channel(appchannelid)
            mysqlconfig = await self.bot.get_shared_api_tokens('mysql')
            sql = await aiomysql.connect(**mysqlconfig)
            cursor: Cursor = await sql.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT quizapps.id, maID, masters.Username, masters.EMail, characterName, quizapps.created_at, ipscore FROM quizapps JOIN masters ON quizapps.maID = masters.id WHERE quizapps.state = 0")

            application_ids = []
            if cursor.rowcount != 0:
                data = await cursor.fetchall()
                for row in data:
                    application_ids.append(row['id'])
                    if row['id'] not in self.applications:
                        embed = discord.Embed(title="Click here to go to the application", url=f"https://redcountyrp.com/admin/applications/{row['id']}", color=0x008080)
                        embed.set_author(name="RCRP Application", url=f"https://redcountyrp.com/admin/applications/{row['id']}", icon_url=rcrpguild.icon_url)
                        embed.add_field(name="Username", value=row['Username'], inline=True)
                        embed.add_field(name="Email", value=row['EMail'], inline=True)
                        embed.add_field(name="Character ", value=row['characterName'], inline=True)
                        embed.add_field(name="IP Score", value=row['ipscore'], inline=True)
                        embed.timestamp = row['created_at']
                        message: discord.Message = await appchannel.send(embed=embed)
                        self.applications[row['id']] = message.id
            else:
                messages = [message async for message in appchannel.history() if not message.pinned]
                if len(messages) != 0:
                    await appchannel.delete_messages(messages)
                    self.applications.clear()

            if len(self.applications) != 0:
                keys = []
                for key in self.applications:
                    if key not in application_ids:
                        message = await appchannel.fetch_message(self.applications[key])
                        await message.delete()
                        keys.append(key)

                for key in keys:
                    del self.applications[key]

            await appchannel.edit(name=f'applications-{cursor.rowcount}')
        except Exception as e:
            await self.log(f'{e}')

    @check_pending_applications.before_loop
    async def before_check_pending_applications(self):
        await self.bot.wait_until_ready()
