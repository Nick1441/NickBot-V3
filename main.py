from ast import arg
import discord

#Custom PY Files
import functions
import config
#import customPrefix

import json

from discord.ext import commands

#------====== Load Guild Specific Prefix ======------
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]


client = commands.Bot(command_prefix = get_prefix)

#------====== NickBot Startup ======------
@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    await client.change_presence(activity=discord.Game(name = "Creating Myself"))



#------====== Guild Join ======------
@client.event
async def on_guild_join(guild):
    #------====== Custom Prefixes Commands ======------
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(guild.id)] = '.'

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)
    
    #------====== Auto Create VC ======------
    with open("createroom.json", "r") as f:
        AutoVC = json.load(f)

    autoJSON = {"online":"False", "defaultVC":"none"}
    AutoVC[str(guild.id)] = autoJSON

    with open("createroom.json", "w") as f:
        json.dump(AutoVC, f, indent=4)


#------====== Guild Leave ======------
@client.event
async def on_guild_remove(guild):
    #------====== Custom Prefixes Commands ======------
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes.pop(str(guild.id))

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    #------====== Auto Create VC ======------
    with open("createroom.json", "r") as f:
        AutoVC = json.load(f)

    AutoVC.pop(str(guild.id))

    with open("createroom.json", "w") as f:
        json.dump(AutoVC, f, indent=4)


#------====== Custom Prefix Change ======------
@commands.has_permissions(administrator = True)
@client.command()
async def changeprefix(ctx, prefix):
    with open("prefixes.json", "r") as f:
        prefixes = json.load(f)

    prefixes[str(ctx.guild.id)] = prefix

    with open("prefixes.json", "w") as f:
        json.dump(prefixes, f, indent=4)

    await ctx.send(f"changed to {prefix}")


#------====== Auto VC Change/Enable ======------
@client.command()
async def toggleAutoVC(ctx, *args):
    if len(args) == 0 or len(args) >= 2:
        await ctx.send("AutoVC Creation has been Tured Off.")
    else:
        channel = ctx.guild.voice_channels

        found = False

        for i in channel:
            if str(i.id) == args[0]:
                with open("createroom.json", "r") as f:
                    AutoVC = json.load(f)

                autoJSON = {"online":"True", "defaultVC":f"{args[0]}"}
                AutoVC[str(ctx.guild.id)] = autoJSON

                with open("createroom.json", "w") as f:
                    json.dump(AutoVC, f, indent=4)

                newchan = i.name
                await ctx.send(f"Enabeled Auto Create VC for {newchan}")
                found = True

        if not found:
            with open("createroom.json", "r") as f:
                AutoVC = json.load(f)

            autoJSON = {"online":"False", "defaultVC":"None"}
            AutoVC[str(ctx.guild.id)] = autoJSON

            with open("createroom.json", "w") as f:
                json.dump(AutoVC, f, indent=4)
            await ctx.send(f"Channel Not Recognised, Try Agian.")


#------====== On User Join VC ======------
@client.event
async def on_voice_state_update(member, before, after):
    #------====== Auto Create VC ======------

    VCID = discord.utils.get(client.get_all_channels(), name="CREATE ROOM")
    
    vc = client.get_channel(id=VCID.id)

    channel = client.get_channel("")

    if vc.members:
        channel = client.get_channel(969736299974127668)
        await channel.send("THIS WORKS?")
        return




# TESTING
@client.command()
async def test(message):
    with open("createroom.json", "r") as f:
        AutoVC = json.load(f)

    autoJSON = {"online":"False", "defaultVC":"none"}
    AutoVC[str(message.guild.id)] = autoJSON

    with open("createroom.json", "w") as f:
        json.dump(AutoVC, f, indent=4)







# @client.event
# async def on_message(message):
#     if message.author == client.user:       #Checks to See if itself sent the message
#         return

#     if  message.content[0] != '!':          #Checks to see if its a command
#         return
    


#     #await functions.main(message, client)
#     await client.process_commands(message)


# #CUSTOM PREFIX
# @client.command()
# async def setprefix(ctx, prefix):
#     customPrefix.onPrefixChange(ctx, prefix)
#     #client = commands.Bot(command_prefix="!", case_insensitive=True)
#client = commands.Bot(command_prefix=customPrefix.getPrefix, case_insensitive=True)


client.run(config.DISCORD_TOKEN)