import discord
from datetime import datetime
import csv, json, os, time, asyncio
from discord_webhook import DiscordWebhook, DiscordEmbed
from pypresence import Presence

path = os.getcwd()
files = os.listdir(path)

def discord_bot_live():
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    os.system('title "Nike helper | Waiting for upcoming embeds..."')

    def write_to_csv(order_id, order_email):
        export = open(path + '/embed_export.csv', 'a')
        export.write(order_id + "," + order_email + "\n")
        export.close()
        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Details added to csv")

    client = discord.Client(intents=discord.Intents.all())

    @client.event
    async def on_ready():
        webhook = DiscordWebhook(url = config['webhook_url'])
        embed = DiscordEmbed(title = 'Monitoring #' + config['monitor_channel_name'] + ' channel\nGood luck on drop', color = 15815972)
        embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
        webhook.add_embed(embed)
        response = webhook.execute()
        print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Waiting for upcoming embeds...")

    @client.event
    async def on_message(message):
        if message.channel.name == str(config['monitor_channel_name']):
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
                
    client.run(config['discord_bot_token'], log_handler=None)