import os
import discord
from discord.ext import commands
import new_house

client = commands.Bot(command_prefix = '.')


@client.event
async def on_ready():
    print('starting')

@client.event
async def on_message(message):
    print(message.content)

    mentioned_ids = [mention.id for mention in message.mentions]
    if client.user.id in mentioned_ids:
        print("bot was mentioned, checking if supported link")
        house_data_obj = new_house.scrape_house(message.content)
        house_data_obj.data.pop('Link')


        msg = "***New House Added to Spreadsheet*** \n"
        for key, value in house_data_obj.data.items():
            msg += f"{key}: {value}\n"

        if 'zillow.com' in house_data_obj.full_link:
            await message.channel.send("We cant get all data from zillow but still added limited data to the sheet")

        await message.channel.send(msg)




#client.run('NzM4NTUwMTQzNTM1ODA4NjEz.XyNiaw.2m2l2Cy3w4khkP1rDKFgS4N_iWU')
client.run(os.environ['DISCORD_TOKEN'])