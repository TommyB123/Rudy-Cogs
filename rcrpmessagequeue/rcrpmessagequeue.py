import discord
import asyncio
import aiomysql
from redbot.core import commands
from .config import mysqlconfig
from .utility import rcrpguildid, adminchat, helperchat

class RCRPMessageQueue(commands.Cog, name="RCRP Message Queue"):
    def __init__(self, bot):
        self.bot = bot
        self.bot.loop.create_task(self.process_message_queue)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.guild.id == rcrpguildid and message.author.id != self.bot.user.id:
            if message.channel.id == adminchat or message.channel.id == helperchat:
                queuemessage = f"{message.author.name} (discord): {message.content}"
                sql = await aiomysql.connect(**mysqlconfig)
                cursor = await sql.cursor()
                await cursor.execute("INSERT INTO messagequeue (channel, message, origin, timestamp) VALUES (%s, %s, 2, UNIX_TIMESTAMP())", (message.channel.id, queuemessage))
                await cursor.close()
                sql.close()
    
    async def process_message_queue(self):
        while 1:
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT id, channel, message FROM messagequeue WHERE origin = 1 ORDER BY timestamp ASC")

            delete = []
            results = await cursor.fetchall()
            for message in results:
                channel = self.bot.get_channel(int(message['channel']))
                if message['message']:
                    try:
                        escapedmessage = discord.utils.escape_mentions(message['message'])
                        await channel.send(escapedmessage)
                    except:
                        print("invalid message content detected")
                delete.append(message['id'])

            for messageid in delete:
                await cursor.execute("DELETE FROM messagequeue WHERE id = %s", (messageid, ))

            await cursor.close()
            sql.close()
            await asyncio.sleep(1) #checks every second
