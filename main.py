import os
import discord
from discord.ext import commands
from pytubefix import YouTube

from pteroadmin import PteroClient
from secret import BOT_TOKEN
from sql import Database

#CONFIG

database = Database()
bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for /website"))
    await bot.sync_commands()

#Pterodactyl

@bot.slash_command(
    name="link",
    description="Link your account to Pterodactyl"
)
async def link(ctx, email: str, api_key: str, force_relink: bool = False):
    #TODO!
    # Check if user already in database
    # Then Check if their API works

    if not force_relink and database.find_user_by_email(email):
        await ctx.respond("You are already linked according to the database; if you like to force link then put 'True' on Force Link Paramenter")
    elif database.find_user_by_discord_id(ctx.author.id):
        await ctx.respond("Somebody with a different discord id has already linked")
    else:
        user = PteroClient(api_key=api_key, email=email)
        User = user.checkAPI(discord_id=ctx.author.id)

        if User == None:
            await ctx.respond("The API key provided did not work.")
        else:
            database.add_user(User)
            await ctx.respond("Added to database!")

        

# Misc.
@bot.slash_command(
    name="website",
    description="Shares information regarding website"
)
async def website(ctx):
    embed=discord.Embed(title="🧭 Compass", color=0xFFD700)
    embed.add_field(name="Main Website", value="https://hyspeedhosting.com/", inline=False)
    embed.add_field(name="Control Panel", value="https://control.hyspeedhosting.com/", inline=False)
    embed.add_field(name="Status Page", value="https://status.hyspeedhosting.com/", inline=True)
    await ctx.respond(embed=embed)

def downloadYoutube(link):
    try: 
        # object creation using YouTube 
        yt = YouTube(link) 
    except: 
        #to handle exception 
        print("Connection Error") 

    yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(filename="video.mp4")
    return yt 

@bot.slash_command(
    name="download",
    description="Download youtube video"
)
async def download(ctx, url: str):
    try: 
        video = YouTube(url) 
        video.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first().download(filename="video.mp4")
        video = downloadYoutube(link=url)
        await ctx.respond("Video downloaded... uploading...")
        await ctx.send(file=discord.File("video.mp4"))
        os.remove("video.mp4")
    except: 
        ctx.respond("Error in downloading video...")


    

#TODO!
# Pterodactyl
# ❌ Link Function (in progress)
#   ❌ Database System
#   ❌ User Classes
# ❌ Server Navbar

# Run the bot with your token
bot.run(BOT_TOKEN)
