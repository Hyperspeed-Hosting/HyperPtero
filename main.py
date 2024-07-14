import asyncio
import json
import os
from time import sleep, time
import discord
from discord.ui import Button, View, Select
from Pythactyl.Admin import PterodactylAdmin
from pydactyl import PterodactylClient
import websockets
import threading

from embed import manageServerEmbed
from secret import BOT_TOKEN, PTERO_API


class Database():
    __LOCATION__ = "database.json"
    def __init__(self) -> None:
        self.location = self.__LOCATION__
        
        if not os.path.exists(self.location):
            with open(self.location, 'w') as db_file:
                json.dump({}, db_file)
    
    def createUser(self, discordId: int, pterodactylId: int, api_key: str):
        # Read existing data
        with open(self.location, 'r') as db_file:
            data = json.load(db_file)
        
        # Update the data with the new user
        data[discordId] = {"pteroId": pterodactylId, "api_key": api_key}
        
        # Write the updated data back to the JSON file
        with open(self.location, 'w') as db_file:
            json.dump(data, db_file, indent=4)
        
    def userExists(self, discordId: int, api_key: str) -> bool:
        with open(self.location, 'r') as db_file:
            data = json.load(db_file)
            user = data.get(str(discordId))
            if user and user.get("api_key") == api_key:
                return True
        return False

    def findApikey(self, discordId:int) -> str:
        with open(self.location, 'r') as db_file:
            data = json.load(db_file)
            try:
                user = data.get(str(discordId))
                return user["api_key"]
            except:
                return None
        return None

database = Database()

class PteroAdmin():
    def __init__(self) -> None:
        self.link = "https://control.hyspeedhosting.com"
        self.api_key = PTERO_API
        self.adminAPI = PterodactylAdmin(self.link, self.api_key)
    
    def locateUserByEmail(self, email: str) -> int:
        for i, user in enumerate(self.adminAPI.listUsers(), start=1):
            if user.email == email:
                return i+1
        return -1

    def verifyFunctionality(self, api: str) -> bool:
        try:
            api = PterodactylClient("https://control.hyspeedhosting.com", api)
            my_servers = api.client.servers.list_servers()
            return True #True because it managed to collect data
        except Exception as e:
            print(e)
            return False


adminApi =  PteroAdmin()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")


@bot.slash_command(
    name="hi",
    description="Provide your email and API key."
)
async def hi(ctx):
    await ctx.respond("Hi")


#linking process
@bot.slash_command(
    name="link",
    description="Provide your email and API key."
)
async def link(ctx, email: str, api_key: str):
    if database.userExists(ctx.author.id, api_key=api_key):
        await ctx.respond("You already exist!")
    else:
        user_id = adminApi.locateUserByEmail(email=email)
        
        if user_id == -1:
            await ctx.respond("We could not find your email on our database...")
        
        if not adminApi.verifyFunctionality(api=api_key):
            await ctx.respond("Double Check API key. It did not work.")

        database.createUser(ctx.author.id, user_id, api_key=api_key)
        await ctx.respond("SUCCESSFULLY LINKED!")

#server manipulation
@bot.slash_command(
    name="servers",
    description="Locates all your servers"
)
async def servers(ctx, i: int = 0): 
    #i: int = 0 #list on server
    clientKey = database.findApikey(ctx.author.id)
    if clientKey == None:
        await ctx.respond("You did not link.")

    view = View()
    
    
    api = PterodactylClient("https://control.hyspeedhosting.com", clientKey)
    data = api.client.servers.list_servers().data
    
    class CounterView(discord.ui.View):
        def __init__(self):
            super().__init__(timeout=None)
            self.count = i
            self.update_buttons()

        def update_buttons(self):
            if (self.count == len(data) - 1):
                self.increment_button.disabled = True
            else:
                self.increment_button.disabled = False
            
            if (self.count == 0):
                self.decrement_button.disabled = True
            else:
                self.decrement_button.disabled = False
            #self.increment_button.disabled = self.count == len(data) - 1
            #self.decrement_button.disabled = self.count >= 0
            # self.decrement_button.enabled = True

        async def update_embed(self, interaction: discord.Interaction):
            self.update_buttons()
            await interaction.message.edit(embed=manageServerEmbed(data[self.count]["attributes"], api=api), view=self)
            await interaction.response.defer()

        @discord.ui.button(label="⬅️", style=discord.ButtonStyle.danger)
        async def decrement_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.count -= 1
            await self.update_embed(interaction)

        @discord.ui.button(label="➡️", style=discord.ButtonStyle.primary)
        async def increment_button(self, button: discord.ui.Button, interaction: discord.Interaction):
            self.count += 1
            await self.update_embed(interaction)
        
    view = CounterView()


    await ctx.respond(embed=manageServerEmbed(data[0]["attributes"], api=api), view=view) 




class ConsoleView(discord.ui.View):
    def __init__(self, api: PterodactylClient, server, bot):
        super().__init__(timeout=None)
        self.api: PterodactylClient = api
        self.server = server[0]["attributes"]
        self.update_buttons()
        self.thread = threading.Thread(target=self.start_monitoring, daemon=True)
        self.thread.start()
    
    def getStatus(self):
        return self.api.client.servers.get_server_utilization(server_id=self.server["identifier"])["current_state"]

    def update_buttons(self, changing: bool = False):
        if changing: #in a state where it's changing, wait for it to finish
            self.stop.disabled = True
            self.start.disabled = True
        else:
            if self.getStatus() == "offline":
                self.stop.disabled = True
                self.start.disabled = False
            else:
                self.stop.disabled = False
                self.start.disabled = True

    async def update_embed(self, interaction: discord.Interaction):
        embed = manageServerEmbed(server=self.server, api=self.api)
        self.update_buttons()
        await interaction.message.edit(embed=embed, view=self)
        await interaction.response.defer()

    @discord.ui.button(label="Start", style=discord.ButtonStyle.green)
    async def start(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.api.client.servers.send_power_action(self.server["identifier"], "start")
        print("POWER IS SENT")
        self.update_buttons(changing=True)
        await self.update_embed()
        await interaction.response.defer()
    
    @discord.ui.button(label="Stop", style=discord.ButtonStyle.danger)
    async def stop(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.api.client.servers.send_power_action(self.server["identifier"], "kill")
        self.update_buttons(changing=True)
        await self.update_embed()
        await interaction.response.defer()

    def start_monitoring(self): #this will go on for 1 hour
        start_time = time()
        while True:
            print(f"Update...; The status is {self.getStatus()}")
            asyncio.run(self.update_embed())
            sleep(3)
            # Stop after 1 hour
            if time() - start_time > 3600:
                break

@bot.slash_command(
    name="manage",
    description="Manage the Console API of a Server"
)
async def manage(ctx, server_id: int = -1):
    clientKey = database.findApikey(ctx.author.id)
    if clientKey == None:
        await ctx.respond("You did not link.")
    
    api = PterodactylClient("https://control.hyspeedhosting.com", clientKey)
    data = api.client.servers.list_servers().data
    #many = len(data) > 1

    #if server_id == -1 and many: #if user has many servers
    #    stringBuilder = ""
    #    i = 0
    #    for server in data:
    #        print(server["attributes"]["name"])
    #        stringBuilder += f"Server ID: {i}\n"
    #        stringBuilder += f"Server Name: {server["attributes"]["name"]}\n"
    #        i += 1
    #    await ctx.respond(f"You will need to identify a server you own. Use ``/servers`` or identify the ones you own:\n{stringBuilder}") 
    
    server_id = 0
    #server = data[server_id]["attributes"]["identifier"]
    #status = api.client.servers.get_server_utilization(server_id=server)
    
    view = ConsoleView(api=api, server=data, bot= bot)
    #TODO!
    await ctx.respond(embed=manageServerEmbed(data[0]["attributes"], api), view=view)

@bot.slash_command(
    name="status",
    description="Embed; Shows Details Server"
)
async def status(ctx):
    clientKey = database.findApikey(ctx.author.id)
    if clientKey == None:
        await ctx.respond("You did not link.")
    
    api = PterodactylClient("https://control.hyspeedhosting.com", clientKey)
    data = api.client.servers.list_servers().data
    many = len(data) > 1 #if over 1 server

    embed = manageServerEmbed(data[0]["attributes"], api=api)

    response = await ctx.respond(embed=embed)
    #original_message = await ctx.fetch_message(response.id)
    
    for field in embed.fields:
        if field.name == "name":
            field.value = "TESTTEST"
            break
    
    while True:
        sleep(2)
        await ctx.interaction.edit_original_response(embed=manageServerEmbed(data[1]["attributes"], api=api))

    #TODO!
    # edit pre-existing embed

# Run the bot with your token
bot.run(BOT_TOKEN)
