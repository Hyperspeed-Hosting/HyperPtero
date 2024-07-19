import discord

#CONFIG
BOT_TOKEN = "GOES HERE"

bot = discord.Bot()

@bot.event
async def on_ready():
    print(f"We have logged in as {bot.user}")
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name="for /website"))

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

# Run the bot with your token
bot.run(BOT_TOKEN)
