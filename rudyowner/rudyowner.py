import discord
import aiomysql
from redbot.core import commands
from .config import mysqlconfig

#weapon origins
origins = {
    1: "Admin Refunded Weapons",
    2: "Illegal Weapons",
    3: "Faction Weapons",
    4: "Licensed Weapons",
    7: "Storebought Items",
    8: "Strawman Weapons"
}

#weapon names
weaponnames = {
    0: "Fist",
    1: "Brass Knuckles",
    2: "Golf Club",
    3: "Nightstick",
    4: "Knife",
    5: "Baseball Bat",
    6: "Shovel",
    7: "Pool Cue",
    8: "Katana",
    9: "Chainsaw",
    10: "Purple Dildo",
    11: "Small White Vibrator",
    12: "Big White Vibrator",
    13: "Small Silver Vibrator",
    14: "Flowers",
    15: "Cane",
    16: "Grenade",
    17: "Teargas",
    18: "Molotov Cocktail",
    19: "",
    20: "",
    21: "Heavy Armor",
    22: "9mm",
    23: "Silenced Pistol",
    24: "Desert Eagle",
    25: "Shotgun",
    26: "Sawn-off Shotgun",
    27: "SPAS-12",
    28: "Micro Uzi (Mac 10)",
    29: "MP5",
    30: "AK-47",
    31: "M4",
    32: "Tec9",
    33: "Country Rifle",
    34: "Sniper Rifle",
    35: "Rocket Launcher (RPG)",
    36: "Heat-Seeking Rocket Launcher",
    37: "Flamethrower",
    38: "Minigun",
    39: "Satchel Charges",
    40: "Detonator",
    41: "Spray Can",
    42: "Fire Extinguisher",
    43: "Camera",
    44: "Night Vision Goggles",
    45: "Thermal Goggles",
    46: "Parachute",
    47: "",
    48: "",
    49: "",
    50: "",
    51: "",
    52: "",
    53: "",
    54: "",
    55: "Beanbag Shotgun"
}

class OwnerCog(commands.Cog):
    """Cog containing owner commands for the RCRP discord"""

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def dms(self, ctx: commands.Context):
        """Gives an imgur album showing why my DMs are not open."""
        await ctx.send("<https://imgur.com/a/yYK5dnZ>")

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def legit(self, ctx: commands.Context):
        """Proof of riches"""
        await ctx.send('MY CASH IS LEGIT BABY https://i.imgur.com/z5pwmj4.gifv')

    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def economy(self, ctx: commands.Context):
        """Collects statistics about the server's economy"""
        async with ctx.typing():
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT SUM(Bank) AS Bank, SUM(Check1) AS CheckSlot1, SUM(Check2) AS CheckSlot2, SUM(Check3) AS CheckSlot3 FROM players")
            playerdata = await cursor.fetchone()
            await cursor.execute("SELECT SUM(BankBalance) AS FBank FROM factions WHERE id != 3")
            factionbank = await cursor.fetchone()
            await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_player WHERE item = 45")
            inhandcash = await cursor.fetchone()
            await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_house WHERE item = 45")
            housecash = await cursor.fetchone()
            await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_bizz WHERE item = 45")
            bizzcash = await cursor.fetchone()
            await cursor.execute("SELECT SUM(itemval) AS dollars FROM inventory_vehicle WHERE item = 45")
            vehiclecash = await cursor.fetchone()
            cashsum = inhandcash['dollars'] + playerdata['Bank'] + playerdata['CheckSlot1'] + playerdata['CheckSlot2'] + playerdata['CheckSlot3'] + factionbank['FBank'] + housecash['dollars'] + bizzcash['dollars'] + vehiclecash['dollars']
            await cursor.close()
            sql.close()

            embed = discord.Embed(title = 'RCRP Economy Statistics', color = 0xe74c3c, timestamp = ctx.message.created_at)
            embed.add_field(name = "In-Hand Cash", value = '${:,}'.format(inhandcash['dollars']))
            embed.add_field(name = "Player Banks", value = '${:,}'.format(playerdata['Bank']))
            embed.add_field(name = "Check Slot 1", value = '${:,}'.format(playerdata['CheckSlot1']))
            embed.add_field(name = "Check Slot 2", value = '${:,}'.format(playerdata['CheckSlot2']))
            embed.add_field(name = "Check Slot 3", value = '${:,}'.format(playerdata['CheckSlot3']))
            embed.add_field(name = 'Faction Banks (excluding ST)', value = '${:,}'.format(factionbank['FBank']))
            embed.add_field(name = 'Stored House Cash', value = '${:,}'.format(housecash['dollars']))
            embed.add_field(name = 'Stored Business Cash', value = '${:,}'.format(bizzcash['dollars']))
            embed.add_field(name = 'Stored Vehicle Cash', value = '${:,}'.format(vehiclecash['dollars']))
            embed.add_field(name = 'Total', value = '${:,}'.format(cashsum))
            await ctx.send(embed = embed)
    
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def drugs(self, ctx: commands.Context):
        """Collects statistics related to how many drugs are on the server"""
        async with ctx.typing():
            drugs = {47:0, 48:0, 49:0, 51:0, 52:0, 53:0, 55:0, 57:0}
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor(aiomysql.DictCursor)
            await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_player WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
            results = await cursor.fetchall()

            for drug in results:
                drugs[drug['item']] += drug['items']

            await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_house WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
            results = await cursor.fetchall()

            for drug in results:
                drugs[drug['item']] += drug['items']

            await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_bizz WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
            results = await cursor.fetchall()

            for drug in results:
                drugs[drug['item']] += drug['items']

            await cursor.execute("SELECT SUM(itemval) AS items, item FROM inventory_vehicle WHERE item IN (47, 48, 49, 51, 52, 53, 55, 57) GROUP BY item")
            results = await cursor.fetchall()

            for drug in results:
                drugs[drug['item']] += drug['items']
            
            await cursor.close()
            sql.close()

            embed = discord.Embed(title = 'RCRP Drug Statistics', color = 0xe74c3c, timestamp = ctx.message.created_at)
            embed.add_field(name = 'Low Grade Cocaine', value = '{:,}'.format(drugs[47]))
            embed.add_field(name = 'Medium Grade Cocaine', value = '{:,}'.format(drugs[48]))
            embed.add_field(name = 'High Grade Cocaine', value = '{:,}'.format(drugs[49]))
            embed.add_field(name = 'Low Grade Crack', value = '{:,}'.format(drugs[51]))
            embed.add_field(name = 'Medium Grade Crack', value = '{:,}'.format(drugs[52]))
            embed.add_field(name = 'High Grade Crack', value = '{:,}'.format(drugs[53]))
            embed.add_field(name = 'Marijuana', value = '{:,}'.format(drugs[55]))
            embed.add_field(name = 'Heroin', value = '{:,}'.format(drugs[57]))
            await ctx.send(embed = embed)
    
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def weapons(self, ctx: commands.Context, origin: int):
        """Queries the database for weapon statistics depending on its origin"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT COUNT(*) AS count, WeaponID FROM weapons WHERE WeaponOrigin = %s AND Deleted = 0 GROUP BY WeaponID ORDER BY WeaponID", (origin, ))

        if cursor.rowcount == 0:
            await ctx.send("Invalid origin type.")
            await cursor.close()
            sql.close()
            return

        results = await cursor.fetchall()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = f'RCRP Weapon Statistics ({origins[origin]})', color = 0xe74c3c, timestamp = ctx.message.created_at)
        for weapon in results:
            embed.add_field(name = weaponnames[weapon['WeaponID']], value = '{:,}'.format(weapon['count']))
        await ctx.send(embed = embed)
    
    @commands.command()
    @commands.guild_only()
    @commands.is_owner()
    async def mysql(self, ctx, *, query: str):
        """Sends a MySQL query straight to the RCRP database"""
        async with ctx.typing():
            sql = await aiomysql.connect(**mysqlconfig)
            cursor = await sql.cursor()
            if query.lower().find("update") or query.lower().find("delete"):
                await cursor.execute(query)
                await ctx.send(f'{cursor.rowcount} {"rows" if cursor.rowcount != 1 else "row"} affected.')
            else:
                await cursor.execute(query)
                data = None
                if cursor.rowcount == 0:
                    await ctx.send("No results.")
                    return
                elif cursor.rowcount == 1:
                    data = await cursor.fetchone()
                else:
                    data = await cursor.fetchall()
                
                string = []
                for row in data:
                    string.append(f'{row}\n')
                string = ''.join(string)
                string = string.replace('(', '')
                string = string.replace(')', '')
                await ctx.send(string)
            
            await cursor.close()
            sql.close()
