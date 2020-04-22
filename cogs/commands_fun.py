import discord
import time
import random
from utility import admin_check
from string import ascii_lowercase
from discord.ext import commands

gaslinks = [
    'https://i.imgur.com/iuuFvBb.jpg',
    'https://cdn.discordapp.com/attachments/477293251737550861/577684575388565541/tWzddexCr7NKfzYKafUY33wUuzYw56GvwVsOiEyrGMQ.png',
    'https://cdn.discordapp.com/attachments/639337212424617994/645094552222433280/tumblr_nw2t03DKNH1ufq0ayo1_1280.png',
    'https://cdn.discordapp.com/attachments/639337212424617994/645095656930934784/itsuki-takumi-iketani-at-gas-station-initial-d.png'
]

#the age of rudy. used for the fancy time delta in the age command
rudyage = 1409529600

def pretty_time_delta(seconds):
    sign_string = '-' if seconds < 0 else ''
    seconds = abs(int(seconds))
    years, seconds = divmod(seconds, 31556952)
    days, seconds = divmod(seconds, 86400)
    hours, seconds = divmod(seconds, 3600)
    minutes, seconds = divmod(seconds, 60)
    if years > 0:
        return '%s%dy %dd %dh %dm %ds' % (sign_string, years, days, hours, minutes, seconds)
    elif days > 0:
        return '%s%dd %dh %dm %ds' % (sign_string, days, hours, minutes, seconds)
    elif hours > 0:
        return '%s%dh %dm %ds' % (sign_string, hours, minutes, seconds)
    elif minutes > 0:
        return '%s%dm %ds' % (sign_string, minutes, seconds)
    else:
        return '%s%ds' % (sign_string, seconds)

class FunCmdsCog(commands.Cog, name="Fun"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Gives Rudy a number of different items")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def give(self, ctx, item = 'none'):
        if item == 'poptart':
            await ctx.send("* Rudy enjoys the poptart but vomits it back up about twenty minutes later. * (this actually happened i fucking hate my sister)")
        elif item == 'treat':
            await ctx.send("* Rudy takes the treat from your hand and runs off into another room with it, more than likely a room that has carpet. He chews on the treat clumsily, creating a mess of crumbs on the floor. He eventually sniffs out the crumbs he failed to ingest and finishes off every last one. *")
        elif item == 'bone':
            await ctx.send("* Rudy happily takes the bone from you and runs off with it, however he neglects to actually chew on said bone. He instead leaves the bone in an accessible location at all times and waits for moments of opportune happiness or excitement (e.g, someone returning home) to put it back in his mouth. Once peak excitement levels are reached, he prances around the house with the bone in his mouth, doing multiple laps around the kitchen with it as well. *")
        else:
            await ctx.send("*Rudy stares at your empty hand disappointed. *")

    @commands.command(help = "Sends a stupid message entirely of emojis")
    @commands.guild_only()
    @commands.check(admin_check)
    async def emojisay(self, ctx, *, message:str = None):
        if str is None:
            await ctx.send("Usage: !emojisay [message]")
            return

        message = message.lower()
        newmessage = []
        for c in message:
            if c in ascii_lowercase:
                newmessage.append(':regional_indicator_{0}:'.format(c))
            else:
                newmessage.append(c)

        newmessage = ''.join(newmessage)
        await ctx.message.delete()

        if len(newmessage) >= 2000:
            await ctx.send("Final message was too long.")
        else:
            await ctx.send(newmessage)

    @commands.command(help = "Got any anime gas?")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def gasgasgas(self, ctx):
        await ctx.send(random.choice(gaslinks))

    @commands.command(help = "nigga dozed off real quick")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def dozed(self, ctx):
        await ctx.send(file = discord.File('files/dozed.mp3'))

    @commands.command(help = "unforgiveable")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def cunt(self, ctx):
        await ctx.send(file = discord.File('files/cunt.mp3'))

    @commands.command(help = "a tragic tale")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def wheels(self, ctx):
        await ctx.send("Never put wheels on your PC", file = discord.File('files/wheels.mp3'))

    @commands.command(help = "Hey guys, Valero here")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def valero(self, ctx):
        await ctx.send(file = discord.File('files/valero.mp3'))

    @commands.command(help = "Bazinga!")
    @commands.guild_only()
    @commands.cooldown(1, 60)
    async def bazinga(self, ctx):
        await ctx.send(file = discord.File('files/bazinga.mp3'))

    @commands.command(help = "Give Rudy some pets")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def pet(self, ctx, *, location: str = 'None'):
        if location == 'head' or location == 'ears':
            await ctx.send("* You pet Rudy's head, specifically behind the ears. He enjoys this very much and sticks his nose out directly towards you as a reaction to the affection. *")
        elif location == 'lower back':
            await ctx.send("* You give Rudy a nice petting on his lower back, maybe sneaking in some back scratches too. He enjoys this very much and pokes his nose into the air as a reaction to the affection. *")
        else:
            await ctx.send("*You pet Rudy. He thinks it's pretty neat. *")

    @commands.command(help = "Displays the age of Rudy")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def age(self, ctx):
        rudy_age = pretty_time_delta(int(time.time()) - rudyage)
        await ctx.send(f"Rudy's age: {rudy_age}")

    @commands.command(help = "Gives a kind response about Rudy's weight")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def makerudyfat(self, ctx):
       await ctx.send("Rudy can't be fat you fucking subhuman piece of shit.")

    @commands.command(help = "Gives Rudy a nice bellyrub!")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def bellyrub(self, ctx):
       await ctx.send("* You give Rudy a bellyrub. He kicks at your hand like a fucking idiot. *")

    @commands.command(help = "Takes Rudy for a walk")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def walk(self, ctx):
       await ctx.send("* Upon hearing news of a potential walk, Rudy fucking loses his shit and starts to jump at you like a madman. He pants heavily while jumping at you repeatedly until you hopefully grab his leash and take him on a nice walk through the nearby park. *")

    @commands.command(help = "Displays the weight of Rudy.")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def weight(self, ctx):
       await ctx.send("I weigh 12 pounds. (5.44 KG or 0.85 stone for foreign people)")

    @commands.command(help = "Orders Rudy to sit")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def sit(self, ctx):
       await ctx.send("* Rudy obediently sits down like a good boy. His tail wags back and forth a few times as well. *")

    @commands.command(help = "Orders Rudy to stay")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def stay(self, ctx):
       await ctx.send("* Rudy sits down at his current position with one ear straight up and the other floppy. He eventually gets dog brain syndrome and stands up, following you. *")

    @commands.command(help = "A terrible story from a terrible night")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def brisket(self, ctx):
       await ctx.send("Once upon a time, I wad fed copious amounts of delicious brisket by a drunk man. I have a really sensitive stomach and I'm only supposed to eat special dog food which helps relax it. During the middle of the night when I was asleep, I felt a pain in my stomach and started to cough and gag a bunch. My owner woke up due to the sounds and quickly rushed me into the kitchen in hopes to take me outside. I then proceeded to projectile vomit on the floor several times, it was not a fun experience. My poor owner had to clean up the mess I created. I haven't been fed table food since.")

    @commands.command(help = "A terrible story about some rabbits")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def rabbits(self, ctx):
        await ctx.send("Once upon a time, there was a rabbit that kept intruding in the back yard every once in a while. Every time I noticed it, I would sprint off towards it for reasons my dog brain can't explain. One day I was sniffing around the yard and noticed a bunch of little baby rabbits in a hole dug in MY YARD. My instinctive dog reaction was to murder every single little rabbit that I could find. I even ripped two of them in half with my dog teeth.")

    @commands.command(help = "Give Rudy a bath!")
    @commands.cooldown(1, 60)
    @commands.guild_only()
    async def bathe(self, ctx):
        await ctx.send("* You give Rudy a bath. He dislikes it heavily. *")

    @commands.command(help = "Sends the unix timestamp for Melvin (It's not -1)")
    @commands.guild_only()
    async def unixtimestamp(self, ctx):
        value = int(time.time())
        await ctx.send(f"CURRENT UNIX TIMESTAMP VALUE: {value}")

    @commands.command(help = "Bruh")
    @commands.guild_only()
    async def bruh(self, ctx):
        await ctx.send("https://i.imgur.com/7QWYKgO.jpg")

def setup(bot):
    bot.add_cog(FunCmdsCog(bot))