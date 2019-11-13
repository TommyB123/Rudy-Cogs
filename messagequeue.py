import discord
import mysql.connector
from discord.ext import commands
from utility import rcrp_utility
from mysqlinfo import mysqlconfig

class MsgQueueCog(commands.Cog, name="RCRP Message Queue"):
    def __init__(self, bot):
        self.bot = bot

    async def ProcessMessageQueue(self):
        while 1:
            sql = mysql.connector.connect(** mysqlconfig)
            cursor = sql.cursor(dictionary = True)
            cursor.execute("SELECT id, channel, message FROM messagequeue WHERE origin = 1 ORDER BY timestamp ASC")

            delete = []
            for message in cursor:
                channel = self.bot.get_channel(int(message['channel']))
                if message['message']:
                    await channel.send(message['message'])
                delete.append(message['id'])

            for messageid in delete:
                cursor.execute("DELETE FROM messagequeue WHERE id = %s", (messageid, ))

            sql.commit()
            cursor.close()
            sql.close()
            await asyncio.sleep(1) #checks every second

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.loop.create_task(ProcessMessageQueue(self))

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild is not None:
            if message.channel.id == rcrp_utility.adminchat() or message.channel.id == rcrp_utility.helperchat():
                queuemessage = f"{message.author.name} (discord): {message.content}"
                sql = mysql.connector.connect(** mysqlconfig)
                cursor = sql.cursor()
                cursor.execute("INSERT INTO messagequeue (channel, message, origin, timestamp) VALUES (%s, %s, 2, UNIX_TIMESTAMP())", (message.channel.id, queuemessage))
                sql.commit()
                cursor.close()
                sql.close()

def setup(bot):
    bot.add_cog(MsgQueueCog(bot))