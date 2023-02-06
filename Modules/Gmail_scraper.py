from csv import DictReader
import os, requests, json, time, imaplib, email, quopri, re, base64
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from bs4 import BeautifulSoup


path = os.getcwd()
files = os.listdir(path)

def write_to_csv(tracking_number, tracking_code):
    export = open(path + '/gmail_export.csv', 'a')
    export.write("DPD," + tracking_number + "," + tracking_code + "\n")
    export.close()
    print('Details added to csv')
    time.sleep(2)

def gmail_dpd():
    os.system('title "Nike helper | Scrapping DPD emails"')
    tracking_info = []
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    imap_server = imaplib.IMAP4_SSL('imap.gmail.com')
    imap_server.login(config['gmail_username'], config['gmail_password'])
    imap_server.select('inbox')
    status, messages = imap_server.search(None, "FROM", "NOREPLY@dpd.cz", "UNSEEN")
    message_ids = messages[0].split()
    for message_id in message_ids:
        status, data = imap_server.fetch(message_id, '(RFC822)')
        email_message = email.message_from_string(data[0][1].decode('utf-8'))
        decoded = base64.b64decode(email_message.get_payload()[0].get_payload()).decode('utf-8').replace('\n', '').replace('\r', '')
        soup = BeautifulSoup(decoded, 'html.parser')

        tracking_number = str(soup.find('a')['href']).split('Parcel=')[1]
        code = str(decoded).split('www.dpdkuryr.cz')[1].split('</td>')[0].strip().split('</span></a>, ')[1].split(' ')[2]

        tracking_info.append([tracking_number, code])

    imap_server.close()
    imap_server.logout()

    for order in tracking_info:
        write_to_csv(order[0], order[1])
        time.sleep(1)
    
    webhook = DiscordWebhook(url = config['webhook_url'])
    embed = DiscordEmbed(title = 'Scrapping summary', color = 000000)
    embed.add_embed_field(name = 'Overview:\n', value = '\U0001F69A Scraped ' + str(len(tracking_info)) + ' tracking links', inline = False)
    embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()))
    webhook.add_embed(embed)
    response = webhook.execute()
