import discord
from datetime import datetime
import csv, json, os, time, asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed
from pypresence import Presence
from discord.ext import commands

path = os.getcwd()
files = os.listdir(path)

def discord_bot_past(count):
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    os.system('title "Nike helper | Scrapping {} embeds..."'.format(str(count)))

    intents = discord.Intents.default()
    intents.members = True

    client = commands.Bot(".", intents=discord.Intents.all())
    
    def write_to_csv(order_id, order_email):
        export = open(path + '/embed_export.csv', 'a')
        export.write(order_id + "," + order_email + "\n")
        export.close()
        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Details added to csv")
    
    @client.event
    async def on_ready():
        webhook = DiscordWebhook(url = config['webhook_url'])
        embed = DiscordEmbed(title = 'Scraping {} embeds'.format(count), color = 15815972)
        embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
        webhook.add_embed(embed)
        response = webhook.execute()
        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Scraping {} embeds".format(count))

        os.system('title "Nike helper | Scraping {} embeds..."'.format(count))
        channel_name = config['monitor_channel_name']

        channel = None
        for guild in client.guilds:
            for current_channel in guild.channels:
                if current_channel.name == channel_name:
                    channel = current_channel
                    break
            if channel is not None:
                break
        if channel is None:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Error: Could not find channel with name {}".format(channel_name))
            return

        #messages = await channel.history(limit=int(count)).flatten()

        async for message in channel.history(limit=int(count)):
            try:
                bot = str(message.embeds[0].footer.text)
                if 'uSNKRS' in bot:
                    try:
                        order_id = str(message.embeds[0].fields[5].value).split('||')[1].split('||')[0].strip().replace(' ', '')
                        order_email = str(message.embeds[0].fields[1].value).split('||')[1].split('||')[0].strip().replace(' ', '')
                    except:
                        order_id = str(message.embeds[0].fields[5].value).split('||')[1].split('||')[0].strip()
                        order_email = str(message.embeds[0].fields[1].value).split('||')[1].split('||')[0].strip()
                    write_to_csv(order_id, order_email)
                
                if 'Tohru' in bot:
                    try:
                        order_id = str(message.embeds[0].fields[6].value).split('||')[1].split('||')[0].strip().replace(' ', '')
                        order_email = str(message.embeds[0].fields[7].value).split('||')[1].split('||')[0].strip().replace(' ', '')
                    except:
                        order_id = str(message.embeds[0].fields[6].value).split('||')[1].split('||')[0].strip()
                        order_email = str(message.embeds[0].fields[7].value).split('||')[1].split('||')[0].strip()
                    write_to_csv(order_id, order_email)
                
                if 'KodaiAIO' in bot:
                    try:
                        order_id = str(message.embeds[0].fields[5].value).replace('#', '').split('||')[1].split('||')[0].strip().replace(' ', '')
                        order_email = str(message.embeds[0].fields[6].value).split('\n')[1].split('||')[0].strip().replace(' ', '')
                    except:
                        order_id = str(message.embeds[0].fields[5].value).replace('#', '').split('||')[1].split('||')[0].strip()
                        order_email = str(message.embeds[0].fields[6].value).split('\n')[1].split('||')[0].strip()
                    write_to_csv(order_id, order_email)

            except:
                pass

        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Tracking finished")
        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Restart bot to continue")
                
    client.run(config['discord_bot_token'], log_handler=None)