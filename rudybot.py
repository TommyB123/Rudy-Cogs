import discord
import asyncio
import random
import mysql.connector

from discord.ext import commands
from samp_client import constants
from samp_client.client import SampClient
from imgurpython import ImgurClient
from mysql.connector import errorcode
from random import randint

#discord bot handler
client = commands.Bot(command_prefix='!')

#mysql info
mysqlconfig = {
    'user': 'ucpdev_devsvr',
    'password': '(N#L0}QXEM@m',
    'host': '127.0.0.1',
    'database': 'ucpdev_devsvr',
    'raise_on_warnings': True,
}

try:
    mysql = mysql.connector.connect(** mysqlconfig)

except mysql.connector.Error as err:
  if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
    print("Access to MySQL DB denied")
  elif err.errno == errorcode.ER_BAD_DB_ERROR:
    print("Invalid database")
  else:
    print(err)

#imgur client handler
imclient = ImgurClient('6f85cfd1f822e7b', '629f840ae2bf44b669560b64403c3f8511293777')

#channels where deletions/edits are not logged (management, development, deleted-messages, edited-messages, status)
staffchannels = ['412340704187252748', '388002249013460993', '463595960367579137', '463644249108250635', '406166047167741952', '464899293166305291', '445668156824879123']

#all admin+ role IDs
staffroles = ['293303836125298690', '293441894585729024', '310927289317588992']

#role ID for the verified role
verifiedrole = '293441047244308481'
rudyfriend = '460848362111893505'

dashboardurl = "https://redcountyrp.com/dashboard"

client.remove_command('help')

async def UpdateSAMPInfo():
    with SampClient(address='server.redcountyrp.com', port=7777) as samp:
        sampinfo=samp.get_server_info()
        await client.change_presence(game=discord.Game(name='RCRP (%i/%i players)' % (sampinfo.players, sampinfo.max_players)))

def isverified(user):
    if verifiedrole in [role.id for role in user.roles] or rudyfriend in [role.id for role in user.roles]:
        return True
    else:
        return False

def random_with_N_digits(n):
    range_start = 10**(n-1)
    range_end = (10**n)-1
    return randint(range_start, range_end)

@client.event
async def on_ready():
    print('\nLogged in as {0}'.format(client.user.name))
    print(client.user.id)
    print('------')

    await UpdateSAMPInfo()

@client.event
async def on_message(message):
    if client.user.id == message.author.id:
        return

    await UpdateSAMPInfo()

    if message.channel.is_private == True:
        if message.content.find('verify') != -1:
            list = message.content.split()
            listcount = len(list)

            if listcount == 1: #empty params
                await client.send_message(message.author, "Usage: verify [Master account name] [Verification code]")

            if listcount > 1:
                if list[1] != "verify":
                    cursor = mysql.cursor()
                    cursor.execute("SELECT COUNT(*) FROM masters WHERE discordid = %s", (message.author.id,))
                    data = cursor.fetchone()
                    cursor.close()
                    if data[0] == 0: #account not verified
                        if listcount == 2: #entering account name
                            cursor = mysql.cursor()
                            cursor.execute("SELECT COUNT(*) FROM masters WHERE Username = %s", (list[1], ))
                            data = cursor.fetchone()
                            if data[0] != 0: #account with name found
                                code = random_with_N_digits(10)
                                cursor = mysql.cursor()
                                cursor.execute("UPDATE masters SET discordcode = %s WHERE Username = %s AND discordid IS NULL", (str(code), list[1]))
                                cursor.close()
                                await client.send_message(message.author, "Your verification code has been set! (debug: {0}) Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({1})\nOnce you have found your verification code, use /verify {2} [code] to confirm your account.".format(code, dashboardurl, list[1]))
                            else:
                                await client.send_message(message.author, "Invalid account name.")
                        if listcount == 3: #entering code
                            cursor = mysql.cursor()
                            cursor.execute("SELECT COUNT(*), id AS results FROM masters WHERE discordcode = %s AND Username = %s", (list[2], list[1]))
                            data = cursor.fetchone()
                            cursor.close()
                            if data[0] == 1: #account match
                                discordserver = client.get_server('93142223473905664')
                                discordmember = discordserver.get_member(message.author.id)
                                verified = discord.utils.get(discordserver.roles, id = '293441047244308481')
                                await client.add_roles(discordmember, verified)
                                cursor = mysql.cursor()
                                cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE id = %s", (message.author.id, data[1]))
                                cursor.close()
                                await client.send_message(message.author, "Your account is now verified!")
                            else:
                                await client.send_message(message.author, "Invalid ID.")
                    else:
                        await client.send_message(message.author, "You have already verified your account.")

        else:
            client.send_message(message.author, "I'm a bot. My only use via direct messages is verifying RCRP accounts. Type 'verify [MA name]' to verify your account.")
    else:
        if isverified(message.author):
            await client.process_commands(message)

@client.event
async def on_message_delete(message):
    if message.channel.id not in staffchannels and message.channel.is_private == False:
        channel = client.get_channel('463595960367579137')
        em=discord.Embed(title='Message Deleted', description='Message by <@{0}> in <#{1}> was deleted'.format(message.author.id, message.channel.id))
        em.add_field(name='Message Content', value=message.content, inline=False)
        await client.send_message(channel, embed=em)

@client.event
async def on_message_edit(before, after):
    if before.channel.id not in staffchannels and before.channel.is_private == False:
        if before.content == after.content:
            return

        channel = client.get_channel('463644249108250635')
        em=discord.Embed(title='Message Edited', description='<@{0}> edited a message in <#{1}>'.format(before.author.id, before.channel.id))
        em.add_field(name='Original Message', value=before.content, inline=False)
        em.add_field(name='New Message', value=after.content, inline=False)
        await client.send_message(channel, embed=em)

#@client.event
#async def on_member_update(before, after):
#    if before.roles != after.roles:
#        cursor = mysql.cursor()
#        #check for removed roles and delete them
#        for role in before.roles:
#            if role.id not in after.roles:
#                cursor.execute("DELETE FROM discordroles WHERE discorduser = %s AND discordrole = %s", (before.id, role.id))
#
#        #check for added roles and insert them
#        for role in after.roles:
#            if role.id not in before.roles:
#                #do shit
#                cursor.execute("INSERT INTO discordroles (discorduser, discordrole) VALUES (%s, %s)", (before.id, role.id))
#                mysql.commit()
#
#        cursor.close()

@client.command(pass_context=True)
async def rudypic(ctx):
    if "460848362111893505" in [role.id for role in ctx.message.author.roles]:
        pictures = []
        for image in imclient.get_album_images('WLQku0l'):
            pictures.append(image.link)
        await client.say(random.choice(pictures))
    else:
        await client.say("You can't do that.")

@client.command()
async def give(item = 'none'):
    if item == 'poptart':
        await client.say("* Rudy enjoys the poptart but vomits it back up about twenty minutes later. * (this actually happened i fucking hate my sister)")
    elif item == 'treat':
        await client.say("* Rudy takes the treat from your hand and runs off into another room with it, more than likely a room that has carpet. He chews on the treat clumsily, creating a mess of crumbs on the floor. He eventually sniffs out the crumbs he failed to ingest and finishes off every last one. *")
    elif item == 'bone':
        await client.say("* Rudy happily takes the bone from you and runs off with it, however he neglects to actually chew on said bone. He instead leaves the bone in an accessible location at all times and waits for moments of opportune happiness or excitement (e.g, someone returning home) to put it back in his mouth. Once that happens, he prances around the house with the bone in his mouth, doing multiple laps around the kitchen with it as well. *")
    else:
        await client.say("*Rudy stares at your empty hand disappointed. *")

@client.command(pass_context=True)
async def clear(ctx, *, amount = 'none'):
    if amount == "" or amount == 'none' or amount.isdigit() == False or amount == 0:
        return

    if [role.id in staffroles for role in ctx.message.author.roles]:
        amount = int(amount)
        if amount > 10:
            await client.say("You cannot clear more than 10 messages at once.")
        else:
            messages = []
            async for i in client.logs_from(ctx.message.channel, limit = amount + 1):
                if not i.pinned:
                    messages.append(i)
            await client.delete_messages(messages)

@client.command(pass_context = True)
async def dms(ctx):
    if ctx.message.author.id == '87582156741681152':
        await client.say("https://imgur.com/a/yYK5dnZ")

@client.command(pass_context = True)
async def pet(ctx, *, location = 'none'):
    if location == 'head' or location == 'ears':
        await client.say("* You pet Rudy's head, specifically behind the ears. He enjoys this very much and sticks his nose out directly towards you as a reaction to the affection. *")
    elif location == 'lower back':
        await client.say("* You give Rudy a nice petting on his lower back, maybe sneaking in some back scratches too. He enjoys this very much and pokes his nose into the air as a reaction to the affection. *")
    else:
        await client.say("*You pet Rudy. He thinks it's pretty neat. *")

@client.command(pass_context = True)
async def clearapps(ctx):
    if ctx.message.channel.id == '445668156824879123':
        messages = []
        async for i in client.logs_from(ctx.message.channel):
            if not i.pinned:
                messages.append(i)
        await client.delete_messages(messages)

#simple no parameter/perm check commands
@client.command()
async def makerudyfat():
   await client.say("Rudy can't be fat you fucking subhuman piece of shit.")

@client.command()
async def bellyrub():
   await client.say("* You give Rudy a bellyrub. He kicks at your hand like a fucking idiot. *")

@client.command()
async def walk():
   await client.say("* Upon hearing news of a potential walk, Rudy fucking loses his shit and starts to jump at you like a madman. He pants heavily while jumping at you repeatedly until you hopefully grab his leash and take him on a nice walk through the nearby park. *")

@client.command()
async def weight():
   await client.say("I weigh 12 pounds. (5.44 KG or 0.85 stone for foreign people)")

@client.command()
async def brooks():
   await client.say("https://i.imgur.com/EZGGWRM.png\n* downstairs borks from dog friend Mr. Brooks *")

@client.command()
async def sit():
   await client.say("* Rudy obediently sits down like a good boy. His tail wags back and forth a few times as well. *")

@client.command()
async def stay():
   await client.say("* Rudy sits down at his current position with one ear straight up and the other floppy. He eventually gets dog brain syndrome and stands up, following you. *")

@client.command()
async def brisket():
   await client.say("Once upon a time, I wad fed copious amounts of delicious brisket by a drunk man. I have a really sensitive stomach and I'm only supposed to eat special dog food which helps relax it. During the middle of the night when I was asleep, I felt a pain in my stomach and started to cough and gag a bunch. My owner woke up due to the sounds and quickly rushed me into the kitchen in hopes to take me outside. I then proceeded to projectile vomit on the floor several times, it was not a fun experience. My poor owner had to clean up the mess I created. I haven't been fed table food since.")

@client.command()
async def rabbits():
   await client.say("Once upon a time, there was a rabbit that kept intruding in the back yard every once in a while. Every time I noticed it, I would sprint off towards it for reasons my dog brain can't explain. One day I was sniffing around the yard and noticed a bunch of little baby rabbits in a hole dug in MY YARD. My instinctive dog reaction was to murder every single little rabbit that I could find. I even ripped two of them in half with my dog teeth.")

@client.command()
async def bathe():
    await client.say("* You give Rudy a bath. He dislikes it heavily. *")

client.run("MzAwMDk4MzYyNTI5NTQ2MjQw.DiIZ3w.pU08PJVTvxqfwF-NpunCEeRigd0")

mysql.close()