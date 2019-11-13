import discord
import time

from datetime import datetime
from discord import commands

class FunCmdsCog(commands.Cog, name="Fun Commands"):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(help = "Gives Rudy a number of different items")
    async def give(self, ctx, item = 'none'):
        if item == 'poptart':
            await ctx.send("* Rudy enjoys the poptart but vomits it back up about twenty minutes later. * (this actually happened i fucking hate my sister)")
        elif item == 'treat':
            await ctx.send("* Rudy takes the treat from your hand and runs off into another room with it, more than likely a room that has carpet. He chews on the treat clumsily, creating a mess of crumbs on the floor. He eventually sniffs out the crumbs he failed to ingest and finishes off every last one. *")
        elif item == 'bone':
            await ctx.send("* Rudy happily takes the bone from you and runs off with it, however he neglects to actually chew on said bone. He instead leaves the bone in an accessible location at all times and waits for moments of opportune happiness or excitement (e.g, someone returning home) to put it back in his mouth. Once peak excitement levels are reached, he prances around the house with the bone in his mouth, doing multiple laps around the kitchen with it as well. *")
        else:
            await ctx.send("*Rudy stares at your empty hand disappointed. *")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def dms(self, ctx):
        await ctx.send("<https://imgur.com/a/yYK5dnZ>")

    @commands.command(help = "Give Rudy some pets")
    async def pet(self, ctx, *, location: str = 'None'):
        if location == 'head' or location == 'ears':
            await ctx.send("* You pet Rudy's head, specifically behind the ears. He enjoys this very much and sticks his nose out directly towards you as a reaction to the affection. *")
        elif location == 'lower back':
            await ctx.send("* You give Rudy a nice petting on his lower back, maybe sneaking in some back scratches too. He enjoys this very much and pokes his nose into the air as a reaction to the affection. *")
        else:
            await ctx.send("*You pet Rudy. He thinks it's pretty neat. *")

    @commands.command(help = "Displays the age of Rudy")
    async def age(self, ctx):
        rudy_age = pretty_time_delta(int(time.time()) - rudyage)
        await ctx.send("Rudy's age: {rudy_age}")

    @commands.command(help = "Gives a kind response about Rudy's weight")
    async def makerudyfat(self, ctx):
       await ctx.send("Rudy can't be fat you fucking subhuman piece of shit.")

    @commands.command(help = "Gives Rudy a nice bellyrub!")
    async def bellyrub(self, ctx):
       await ctx.send("* You give Rudy a bellyrub. He kicks at your hand like a fucking idiot. *")

    @commands.command(help = "Takes Rudy for a walk")
    async def walk(self, ctx):
       await ctx.send("* Upon hearing news of a potential walk, Rudy fucking loses his shit and starts to jump at you like a madman. He pants heavily while jumping at you repeatedly until you hopefully grab his leash and take him on a nice walk through the nearby park. *")

    @commands.command(help = "Displays the weight of Rudy.")
    async def weight(self, ctx):
       await ctx.send("I weigh 12 pounds. (5.44 KG or 0.85 stone for foreign people)")

    @commands.command(help = "Orders Rudy to sit")
    async def sit(self, ctx):
       await ctx.send("* Rudy obediently sits down like a good boy. His tail wags back and forth a few times as well. *")

    @commands.command(help = "Orders Rudy to stay")
    async def stay(self, ctx):
       await ctx.send("* Rudy sits down at his current position with one ear straight up and the other floppy. He eventually gets dog brain syndrome and stands up, following you. *")

    @commands.command(help = "A terrible story from a terrible night")
    async def brisket(self, ctx):
       await ctx.send("Once upon a time, I wad fed copious amounts of delicious brisket by a drunk man. I have a really sensitive stomach and I'm only supposed to eat special dog food which helps relax it. During the middle of the night when I was asleep, I felt a pain in my stomach and started to cough and gag a bunch. My owner woke up due to the sounds and quickly rushed me into the kitchen in hopes to take me outside. I then proceeded to projectile vomit on the floor several times, it was not a fun experience. My poor owner had to clean up the mess I created. I haven't been fed table food since.")

    @commands.command(help = "A terrible story about some rabbits")
    async def rabbits(self, ctx):
       await ctx.send("Once upon a time, there was a rabbit that kept intruding in the back yard every once in a while. Every time I noticed it, I would sprint off towards it for reasons my dog brain can't explain. One day I was sniffing around the yard and noticed a bunch of little baby rabbits in a hole dug in MY YARD. My instinctive dog reaction was to murder every single little rabbit that I could find. I even ripped two of them in half with my dog teeth.")

    @commands.command(help = "Give Rudy a bath!")
    async def bathe(self, ctx):
        await ctx.send("* You give Rudy a bath. He dislikes it heavily. *")

    @commands.command(hidden = True)
    async def unixtimestamp(self, ctx):
        time = int(time.time())
        await ctx.send("CURRENT UNIX TIMESTAMP VALUE: {time}")

def setup(bot):
    bot.add_cog(FunCmdsCog(bot))