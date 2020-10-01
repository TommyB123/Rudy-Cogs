import discord
import aiomysql
import aiohttp
import aiofiles
import aiofiles.os
import re
import os
from .config import mysqlconfig
from redbot.core import commands

class pending_model():
    """Pending model data"""
    model_id: int
    reference_model: int
    dff_name: str
    txd_name: str
    model_type: str
    model_path: str

class RCRPModelManager(commands.Cog):
    """RCRP Model Manager"""
    def __init__(self, bot: discord.Client):
        self.bot = bot
        self.models = {} #dict for pending model data. key will be the model's ID
        self.model_urls = [] #list containing each URL that needs to used for downloading
        self.rcrp_model_path = "/home/rudybot/download_testing" #path of RCRP models

    def get_model_range_for_type(self, type: str):
        """Returns the valid range of model IDs for a specific type"""
        type = type.upper()
        if type == 'PED':
            return 20000, 30000
        elif type == 'OBJECT':
            return -30000, -1000
        else:
            return -1, -1
    
    def get_model_type_folder(self, type: str):
        """Returns the folder used for a specific model type"""
        type = type.upper()
        if type == 'PED':
            return 'peds'
        elif type == 'OBJECT':
            return 'objects'
        else:
            return '' 
        
    def model_type_int(self, type: str):
        """Returns the reference constant for model types that's used in the MySQL database/RCRP script"""
        type = type.upper()
        if type == 'PED':
            return 0
        elif type == 'OBJECT':
            return 1
        else:
            return -1
    
    def model_type_name(self, type: int):
        """Returns the reference string for model types based on the constant used in the MySQL database/RCRP script"""
        if type == 0:
            return 'PED'
        elif type == 1:
            return 'OBJECT'
        else:
            return 'INVALID'
    
    async def is_valid_model(self, modelid: int):
        """Queries the MySQL database to see if a model ID exists"""
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        await cursor.execute("SELECT NULL FROM models WHERE modelid = %s", (modelid, ))
        rows = cursor.rowcount
        await cursor.close()
        sql.close()

        return rows != 0
    
    def is_valid_model_type(self, type: str):
        """Checks if the supplied string matches a valid model type. Valid types are 'PED' or 'OBJECT'"""
        temp_type = type.upper()
        if temp_type != 'PED' and temp_type != 'OBJECT':
            return False
        else:
            return True

    @commands.group()
    @commands.guild_only()
    @commands.is_owner()
    async def modelmanager(self, ctx):
        """Manage and add new custom models"""
        pass

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def addmodel(self, ctx: commands.Context, modelid: int, reference_id: int, folder: str, type: str, dff_url: str, txd_url: str):
        """Adds a new model to the pending models list"""
        if self.is_valid_model_type(type) == False:
            await ctx.send('Invalid type.')
            return

        min, max = self.get_model_range_for_type(type)
        if modelid not in range(min, max):
            await ctx.send(f'Invalid model ID for type {type}. Please use a range of {min} to {max} for this type.')
            return
        
        if await self.is_valid_model(modelid) == True:
            await ctx.send(f'The model {modelid} is already present on the server.')
            return
        
        dff_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', dff_url)
        if dff_match == None:
            await ctx.send('Invalid Discord URL formatting for DFF URL.')
            return

        txd_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', txd_url)
        if txd_match == None:
            await ctx.send('Invalid Discord URL formatting for TXD URL.')
            return
        
        txd_name = txd_url.replace(txd_match.group(), '')
        dff_name = dff_url.replace(dff_match.group(), '')

        #add model URLs to the list
        self.model_urls.append(dff_url)
        self.model_urls.append(txd_url)

        #assign pending model data, add it to dict
        model_info = pending_model()
        model_info.model_id = modelid
        model_info.reference_model = reference_id
        model_info.dff_name = dff_name
        model_info.txd_name = txd_name
        model_info.model_type = type
        model_info.model_path = folder
        self.models[modelid] = model_info
        await ctx.send(f'Model ID {modelid} has been added to the pending models list. Use !modelmanager finalize when you are ready to download the pending models to the server and add them in-game.')
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def removependingmodel(self, ctx: commands.Context, modelid: int):
        """Removes a model from the list of current pending models"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in self.models:
            await ctx.send('No pending model found with that ID.')
            return

        del self.models[modelid]
        await ctx.send(f'Model ID {modelid} has been removed from the pending models list.')

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def deletemodel(self, ctx: commands.Context, modelid: int, deletefiles: bool = False):
        """Removes a custom model from database (and optionally, deletes the file itself) (RCRP restart required for full effect)"""
        if await self.is_valid_model(modelid) == False:
            await ctx.send(f'{modelid} is not a model ID that is used on the server.')
            return

        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)

        if deletefiles == True:
            await cursor.execute("SELECT * FROM models WHERE modelid = %s", (modelid, ))
            data = await cursor.fetchone()
            typefolder = self.get_model_type_folder(self.model_type_name(data['modeltype']))
            modelfolder = data['folder']
            model_dff = data['dff_name']
            model_txd = data['txd_name']
            model_path = f'{self.rcrp_model_path}/{typefolder}/{modelfolder}'

            if os.path.isfile(f'{model_path}/{model_dff}'):
                os.remove(f'{model_path}/{model_dff}')
            if os.path.isfile(f'{model_path}/{model_txd}'):
                os.remove(f'{model_path}/{model_txd}')
            
            remaining_files = os.listdir(model_path)
            if len(remaining_files) == 0: #folder is empty, delete it
                os.rmdir(model_path)

        await cursor.execute("DELETE FROM models WHERE modelid = %s", (modelid, ))
        await cursor.close()
        sql.close()
        
        await ctx.send(f'Model {modelid} has been deleted from the MySQL database and will not be loaded on the next server restart.')

    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def viewpendingmodel(self, ctx: commands.Context, modelid: int):
        """Views the information of a pending model that has not been sent to the server yet"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        if modelid not in self.models:
            await ctx.send('No pending model found with that ID.')
            return
        
        model_info: pending_model = self.models[modelid]
        embed = discord.Embed(title = f'Pending Model Information ({modelid})', color = ctx.author.color)
        embed.add_field(name = 'Reference ID', value = model_info.reference_model, inline = False)
        embed.add_field(name = 'TXD File Name', value = model_info.txd_name, inline = False)
        embed.add_field(name = 'DFF File Name', value = model_info.dff_name, inline = False)
        embed.add_field(name = 'Model Type', value = model_info.model_type, inline = False)
        embed.add_field(name = 'Model Path', value = model_info.model_path, inline = False)
        await ctx.send(embed = embed)
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def fetchmodelinfo(self, ctx: commands.Context, modelid: int):
        """Retrieves information about an existing model from the MySQL database"""
        if await self.is_valid_model(modelid) == False:
            await ctx.send(f'{modelid} is not a valid model ID used on the server.')
            return
        
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor(aiomysql.DictCursor)
        await cursor.execute("SELECT * FROM models WHERE modelid = %s", (modelid, ))
        data = await cursor.fetchone()
        await cursor.close()
        sql.close()

        embed = discord.Embed(title = f'Model Information ({modelid})', color = ctx.author.color)
        embed.add_field(name = 'TXD', value = data['txd_name'], inline = False)
        embed.add_field(name = 'DFF', value = data['dff_name'], inline = False)
        embed.add_field(name = 'Model Type', value = self.model_type_name(data['modeltype']), inline = False)
        embed.add_field(name = 'Model Path', value = data['folder'], inline = False)
        await ctx.send(embed = embed)
    
    @modelmanager.command()
    @commands.guild_only()
    @commands.is_owner()
    async def finalize(self, ctx: commands.Context):
        """Downloads all pending models and sends a signal to the RCRP gamemode to check for models that are currently not loaded"""
        if len(self.models) == 0:
            await ctx.send('There are currently no pending models.')
            return

        #convert models dict to a list for easier iterating, then clear the dict
        model_list = list(self.models.values())
        model_count = len(model_list)
        self.models.clear()

        await ctx.send(f'{model_count} {"models" if model_count != 1 else "model"} will now be added to RCRP.')

        #remove any duplicate URLs from the list (for objects that may share the same txd or dff)
        self.model_urls = list(dict.fromkeys(self.model_urls))
        url_count = len(self.model_urls)

        #download!
        await ctx.send(f'Beginning the download of the {url_count} necessary {"files" if url_count != 1 else "file"}.')
        if os.path.exists(f'{self.rcrp_model_path}/temp') == False:
            await aiofiles.os.mkdir(f'{self.rcrp_model_path}/temp')
        async with ctx.typing():
            for url in self.model_urls:
                async with aiohttp.ClientSession() as session:
                    async with session.get(url) as response:
                        if response.status == 200:
                            file_match = re.search('https://cdn.discordapp.com/attachments/[0-9]*/[0-9]*/', url)
                            filename = url.replace(file_match.group(), '')
                            data = await response.read()
                            async with aiofiles.open(f'{self.rcrp_model_path}/temp/{filename}', 'wb') as file:
                                await file.write(data)
            await ctx.send(f'Finished downloading {url_count} {"files" if url_count != 1 else "file"}.')

        await ctx.send('Inserting new models into the MySQL database and moving them to their correct folders.')
        sql = await aiomysql.connect(**mysqlconfig)
        cursor = await sql.cursor()
        async with ctx.typing():
            for model in model_list:
                await cursor.execute("INSERT INTO models (modelid, reference_model, modeltype, dff_name, txd_name, folder) VALUES (%s, %s, %s, %s, %s, %s)",
                    (model.model_id, model.reference_model, self.model_type_int(model.model_type), model.dff_name, model.txd_name, model.model_path))
                originfolder = f'{self.rcrp_model_path}/temp'
                destinationfolder = f'{self.rcrp_model_path}/{self.get_model_type_folder(model.model_type)}/{model.model_path}'

                if os.path.exists(destinationfolder) == False:
                    await aiofiles.os.mkdir(destinationfolder)

                if os.path.isfile(f'{originfolder}/{model.dff_name}') == True and os.path.isfile(f'{destinationfolder}/{model.dff_name}') == False:
                    await aiofiles.os.rename(f'{originfolder}/{model.dff_name}', f'{destinationfolder}/{model.dff_name}')

                if os.path.isfile(f'{originfolder}/{model.txd_name}') == True and os.path.isfile(f'{destinationfolder}/{model.txd_name}') == False:
                    await aiofiles.os.rename(f'{originfolder}/{model.txd_name}', f'{destinationfolder}/{model.txd_name}')

        #remove the temporary directory
        await aiofiles.os.rmdir(f'{self.rcrp_model_path}/temp')

        #tap into the RCRP message queue system to tell the server to check for new models
        await cursor.execute("INSERT INTO messagequeue (channel, message, origin, timestamp) VALUES (-1, 'model', 2, UNIX_TIMESTAMP())")

        await cursor.close()
        sql.close()

        await ctx.send(f'{model_count} {"models" if model_count != 1 else "model"} has been successfully downloaded and put in their appropriate directories. The RCRP game server has been instructed to check for new models.')

    @modelmanager.group()
    @commands.guild_only()
    @commands.is_owner()
    async def set(self, ctx: commands.Context):
        """Set various attributes for an existing model"""
        pass

    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def dff(self, ctx: commands.Context, modelid: int, texturename: str):
        """Updates the DFF of an existing model"""
        await ctx.send('wip')

    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def txd(self, ctx: commands.Context, mdoelid: int, txdname: str):
        """Updates the TXD of an existing model"""
        await ctx.send('wip')
    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def folder(self, ctx: commands.Context, modelid: int, folder: str):
        """Updates the folder of an existing model"""
        await ctx.send('wip')
    
    @set.command()
    @commands.guild_only()
    @commands.is_owner()
    async def type(self, ctx: commands.Context, modelid: int, type: str):
        """Updates the type of an existing model (skin or object)"""
        await ctx.send('wip')
