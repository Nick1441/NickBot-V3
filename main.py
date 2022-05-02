
from cmath import exp
from unittest import expectedFailure
import discord

#Custom PY Files
import youtube_dl
import os
import config
#import customPrefix

import json

from discord.ext import commands

#------====== Load Guild Specific Prefix ======------
def get_prefix(client, message):
    with open('prefixes.json', 'r') as f:
        prefixes = json.load(f)
    return prefixes[str(message.guild.id)]

intents1 = discord.Intents.default()
intents1.members = True

client = commands.Bot(command_prefix = get_prefix, intents=intents1)

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
        with open("createroom.json", "r") as f:
            AutoVC = json.load(f)

        autoJSON = {"online":"False", "defaultVC":f"Null"}
        AutoVC[str(ctx.guild.id)] = autoJSON

        with open("createroom.json", "w") as f:
            json.dump(AutoVC, f, indent=4)

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
    #Joined Channel
    if before.channel == None and after.channel != None:
        await AutoCreateFunc(member, before, after)

    #Swapped Channel
    elif before.channel != None and after.channel != None:
        #Swapped Away from Custom Channels
        try:
            with open("OpenRooms.json", "r") as f:
                OpenRooms = json.load(f)

            if OpenRooms[str(member.guild.id)][str(before.channel.id)]:
                await AutoDeleteFunc(member, before, after)
        except:
            pass

        #Swapped Into Create Room
        try:
            with open("createroom.json", "r") as f:
                AutoVC = json.load(f)

            if AutoVC[str(member.guild.id)]['defaultVC'] == str(after.channel.id):
                await AutoCreateFunc(member, before, after)
        except:
            pass
        
    #User Leaves Channel
    else:
        await AutoDeleteFunc(member, before, after)


#------====== Create Auto VC ======------
async def AutoCreateFunc(member, before, after):
    with open("createroom.json", "r") as f:
        AutoVC = json.load(f)

    if AutoVC[str(member.guild.id)]['online'] == "True":
        if AutoVC[str(member.guild.id)]['defaultVC'] == str(after.channel.id):
            VCname = member.display_name
            try:
                VCname.substr(0, 8)
            except:
                pass

            channel2 = await member.guild.create_voice_channel(VCname)
            await member.move_to(channel2)

            with open("OpenRooms.json", "r") as f:
                OpenRooms = json.load(f)

            try:
                OpenRooms[str(member.guild.id)].pop(str(channel2.id))
                OpenRooms[str(member.guild.id)].update({str(channel2.id):"Null"})
            except:
                guildID = str(member.guild.id)
                data = {guildID:{str(after.channel.id):"Null"}}
                OpenRooms.update(data)

            with open("OpenRooms.json", "w") as f:
                json.dump(OpenRooms, f, indent=4)

#------====== Delete Auto VC ======------
async def AutoDeleteFunc(member, before, after):
    if before.channel:
        with open("OpenRooms.json", "r") as f:
            OpenRooms = json.load(f)

        try:
            if str(before.channel.id) in OpenRooms[str(member.guild.id)]:
                id = before.channel.id
                channel = member.guild.voice_channels

                for i in channel:
                    if str(i.id) == str(id): 
                        await i.delete()

                        #Delete JSON here
                        with open("OpenRooms.json", "r") as f:
                            OpenRooms = json.load(f)
                        
                        OpenRooms[str(member.guild.id)].pop(str(i.id))
                        
                        if OpenRooms[str(member.guild.id)] == {}:
                            OpenRooms.pop(str(member.guild.id))

                        with open("OpenRooms.json", "w") as f:
                            json.dump(OpenRooms, f, indent=4)
        except:
            pass


#------====== Simple Music Bot ======------
@client.command()
async def play(ctx, *args):
    if len(args) == 0 or len(args) >= 2:
        await ctx.send(f"Invalid Input for Play <@{ctx.author.id}>")
    else:
        if ctx.author.voice == None:
            await ctx.send(f"Silly Goose! You're not in a VC! <@{ctx.author.id}>")
        else:
            song_there = os.path.isfile("song.mp3")
            try:
                if song_there:
                    os.remove("song.mp3")
            except PermissionError:
                await ctx.send("Wait for the current playing music to end or use the 'stop' command")
                return
 
            voiceChan = ctx.author.voice.channel.id
            #voiceChan = 970403994675593226
            
            voicechannel = client.get_channel(voiceChan)
            try:
                await voicechannel.connect()
            except:
                pass

            voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
                }],
            }
            
            try:
                with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([str(args[0])])
                for file in os.listdir("./"):
                    if file.endswith(".mp3"):
                        os.rename(file, "song.mp3")
                voice.play(discord.FFmpegPCMAudio("song.mp3"))

            except:
                await ctx.send(f"Error Downloading. Is the Link Correct? <@{ctx.author.id}>")


            
@client.command()
async def leave(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        if voice.is_connected():
            await voice.disconnect()
        else:
            ctx.send(f"Cant stop whats not playing! <@{ctx.author.id}>")
    except:
        pass

@client.command()
async def pause(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        if voice.is_playing():
            await voice.pause()
        else:
            ctx.send(f"Nothing is Playing to pause! <@{ctx.author.id}>")
    except:
        pass

@client.command()
async def resume(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        if voice.is_paused():
            await voice.resume()
        else:
            ctx.send(f"umm yeah, nothing is playing to resume! <@{ctx.author.id}>")
    except:
        pass

@client.command()
async def stop(ctx):
    voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

    try:
        voice.stop()
    except:
        pass



###         
            # server = client.get_guild(ctx.author.guild.id)
            # member = server.guild_members
            # await ctx.send(str(member))
            # user = None
            # for i in users:
            #     #await ctx.send(f"{i.id} -- {ctx.author.id}")
            #     if i.id == ctx.author.id:
            #         user = i
            #         await ctx.send(user)

###
        #else:

            
            #voiceChan = ctx.author.voice.channel.id


            #voiceChannel = discord.utils.get(ctx.guild.voice_channels, name=str(ctx.author.voice.channel.id))
            #voice = discord.utils.get(client.voice_clients, guild=ctx.guild)

            




    #Check to See if other Users are in the channel
    #To Do
    #When user leaves, check against json, if it is. remove it
    #Remove Channels. Remove from JSON.
    #Check to see if other users are there first??



    # VCID = discord.utils.get(client.get_all_channels(), name="CREATE ROOM")
    
    # vc = client.get_channel(id=VCID.id)

    # channel = client.get_channel("")

    # if vc.members:
    #     channel = client.get_channel(969736299974127668)
    #     await channel.send("THIS WORKS?")
    #     return




# TESTING
@client.command()
async def test(ctx):
#------====== Auto Create VC ======------
    with open("OpenRooms.json", "r") as f:
        OpenRooms = json.load(f)

    try:

        OpenRooms[str(ctx.guild.id)].pop(str(ctx.channel.id))
    except:
        print()

    try:
        OpenRooms[str(ctx.guild.id)].update({ctx.channel.id:"test one lads"})
    except:
        test = str(ctx.guild.id)
        new = {test:{"active":"Not real"}}
        OpenRooms.update(new)

    with open("OpenRooms.json", "w") as f:
        json.dump(OpenRooms, f, indent=4)







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