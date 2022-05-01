from datetime import datetime
from turtle import title
import discord
import requests
import typer



#HELP FUNCTIONS
async def displayHelp(message, client):
    self = client.get_user(client.user.id)


    helpEmbed = discord.Embed(title="Help - List of Commands", description=f"<@{message.author.id}>", color=0x0abccc)
    helpEmbed.set_author(name=f"NickBot Help", icon_url=self.avatar_url)

    helpEmbed.add_field(name = "**NASA**", value="""
    -> _APOD_ - Astronomy Picture of the Day for current or given date.
    --> e.g. `!NASA APOD` or `!NASA APOD 1998-12-14`\n
    """, inline = False)

    await message.channel.send(embed=helpEmbed)