import discord
import mysqlinfo
import mysql.connector
import utility

from discord import commands

class VerificationCog(commands.Cog, name="RCRP Verification"):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.guild == None:
            if message.content.find('verify') == -1:
                await message.author.send("I'm a bot. My only use via direct messages is verifying RCRP accounts. Type 'verify [MA name]' to verify your account.")
                return

            params = message.content.split()
            paramcount = len(params)

            if paramcount == 1: #empty params
                await message.author.send("Usage: verify [Master account name]")
                return

            if IsDiscordIDLinked(message.author.id):
                await message.author.send("This Discord account is already linked to an RCRP account.")
                return

            if paramcount == 2: #entering account name
                if isValidMasterAccountName(params[1]) == False:
                    await message.author.send("Invalid account name.")
                    return

                if IsAcceptedMasterAccount(params[1]) == False:
                    await message.author.send("You cannot verify your Master Account if you have not been accepted into the server.\nIf you're looking for help with the registration process, visit our forums at https://forum.redcountyrp.com")
                    return

                code = random_with_N_digits(10)
                sql = mysql.connector.connect(** mysqlconfig)
                cursor = sql.cursor()
                cursor.execute("UPDATE masters SET discordcode = %s WHERE Username = %s AND discordid = 0", (str(code), params[1]))
                cursor.close()
                sql.close()

                await message.author.send("Your verification code has been set! Log in on our website and look for 'Discord Verification Code' at your dashboard page. ({dashboardurl})\nOnce you have found your verification code, send 'verify {params[1]} [code]' to confirm your account.")
            elif paramcount == 3: #entering code
                sql = mysql.connector.connect(** mysqlconfig)
                cursor = sql.cursor()
                cursor.execute("SELECT COUNT(*), id, Helper, Tester, AdminLevel AS results FROM masters WHERE discordcode = %s AND Username = %s", (params[2], params[1]))
                data = cursor.fetchone()
                cursor.close()

                if data[0] == 0: #account doesn't match
                    await message.author.send("Invalid ID.")
                    return

                discordguild = self.bot.get_guild(rcrpguild)
                discordmember = discordguild.get_member(message.author.id)
                discordroles = []
                discordroles.append(discordguild.get_role(verifiedrole))
                if data[2] == 1: #guy is helper
                    discordroles.append(discordguild.get_role(helperrole))
                if data[3] == 1: #guy is tester
                    discordroles.append(discordguild.get_role(testerrole))
                if data[4] != 0: #guy is admin
                    discordroles.append(discordguild.get_role(adminrole))
                if data[4] == 4: #guy is management
                    discordroles.append(discordguild.get_role(managementrole))
                await discordmember.add_roles(*discordroles)

                cursor = sql.cursor()
                cursor.execute("UPDATE masters SET discordid = %s, discordcode = 0 WHERE id = %s", (message.author.id, data[1]))
                cursor.close()
                sql.close()

                await message.author.send("Your account is now verified!")
            else:
                await message.author.send("Usage: verify [Master account name]")

def setup(bot):
    bot.add_cog(VerificationCog(bot))