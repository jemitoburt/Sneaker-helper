from csv import DictReader
import os, requests, json, time
from discord_webhook import DiscordWebhook, DiscordEmbed
import dateutil.parser as dp
from datetime import datetime

path = os.getcwd()
files = os.listdir(path)

def read_csv_nike_track():
    track_data = []
    order_count = 0
    with open(path + '/nike_tracker.csv') as f:
        reader = DictReader(f)
        for line in reader:
            order_number = line['ORDER_NUMBER']
            order_email = line['ORDER_EMAIL']
            track_data.append([order_number, order_email])
            order_count += 1
    os.system('title "Nike helper | Tracking ' + str(order_count) + ' orders"')
    return track_data

def write_to_csv(carrier,tracking_number, zip_code):
    export = open(path + '/carrier_tracker.csv', 'a')
    export.write(carrier + "," + tracking_number + "," + zip_code + "\n")
    export.close()
    time.sleep(1)

def track_nike(track_data):
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    order_shipped = 0
    order_awaiting_ship = 0
    order_delivered = 0
    failed_tracking = 0
    cookies_response = requests.get('https://www.nike.com/orders/details/').cookies

    for order in track_data:
        headers = {
            'authority': 'api.nike.com',
            'accept': 'application/json',
            'nike-api-caller-id': 'com.nike:sse.orders',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36',
        }

        params = {
            'locale': 'en_us',
            'country': 'US',
            'language': 'en',
            'email': order[1],
            'timezone': 'Europe/Amsterdam',
        }
        try:
            response_json = json.loads(requests.get('https://api.nike.com/orders/summary/v1/' + order[0], params=params, headers=headers, cookies=cookies_response).text)
            product_image = response_json['group'][0]['orderItems'][0]['product']['productImage']
            order_date = '<t:' +  str(dp.parse(response_json['transaction']['orderDate'].split('[')[0]).timestamp()).split('.')[0] + '>'
            try:
                product_name = response_json['group'][0]['orderItems'][0]['product']['title'] + ' - ' + str(response_json['group'][0]['orderItems'][0]['product']['size']).split('Size ')[1]
            except:
                product_name = response_json['group'][0]['orderItems'][0]['product']['title'] + ' - ' + str(response_json['group'][0]['orderItems'][0]['product']['size'])
            product_sku =  response_json['group'][0]['orderItems'][0]['product']['styleColor']
            order_status = response_json['group'][0]['heading']
            order_price = str(response_json['transaction']['orderTotal']) + 'EUR'

            tracking_status = response_json['group'][0]['heading']

            if tracking_status == 'Shipped':
                order_shipped += 1

            if 'Delivered' in tracking_status:
                order_delivered += 1

            if response_json['group'][0]['actions'] == {} or tracking_status == 'Preparing shipment':
                order_awaiting_ship += 1
                order_status = 'Order Not shipped yet'
                webhook = DiscordWebhook(url = config['webhook_url'])
                embed = DiscordEmbed(title = order_status, color = 15815972)
                embed.add_embed_field(name = 'Order number', value = '||' + order[0] + '||', inline = False)
                embed.add_embed_field(name = 'Order date', value = order_date, inline = False)
                embed.add_embed_field(name = 'Order email', value = order[1], inline = False)
                embed.add_embed_field(name = 'Product name', value = product_name + '\n' + product_sku, inline = False)
                embed.add_embed_field(name = 'Order price', value = order_price, inline = False)
                embed.set_thumbnail(url = product_image)
                embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
                webhook.add_embed(embed)
                response = webhook.execute()

            elif response_json['group'][0]['heading'] != {}:
                order_status = response_json['group'][0]['heading']
                order_track = response_json['group'][0]['actions']['trackShipment']['webLink']
                if 'UPS' in order_track:
                    carrier = 'UPS'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found UPS tracking, added to csv")
                
                if 'DPD' in order_track:
                    carrier = 'DPD'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found DPD tracking, added to csv")
                
                if 'POST' in order_track:
                    carrier = 'POST_NL'
                    zip_code = response_json['shipFrom']['address']['zipCode']
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found POST_NL tracking, added to csv")
                
                if 'CNP' in order_track:
                    carrier = 'CHRONOPOST'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found CHRONOPOST tracking, added to csv")
                
                if 'DHL' in order_track:
                    carrier = 'DHL'
                    zip_code = response_json['shipFrom']['address']['zipCode']
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found DHL tracking, added to csv")
                
                if 'BRT' in order_track:
                    carrier = 'BRT'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    write_to_csv(carrier,tracking_number, zip_code)
                    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found BRT tracking, added to csv")

                webhook = DiscordWebhook(url = config['webhook_url'])
                embed = DiscordEmbed(title = 'Order ' + order_status, color = 15815972)
                embed.add_embed_field(name = 'Order number', value = '||' + order[0] + '||', inline = False)
                embed.add_embed_field(name = 'Order date', value = order_date, inline = False)
                embed.add_embed_field(name = 'Order email', value = order[1], inline = False)
                embed.add_embed_field(name = 'Product name', value = product_name + '\n' + product_sku, inline = False)
                embed.add_embed_field(name = 'Order price', value = order_price, inline = False)
                embed.add_embed_field(name = 'Order tracking', value = '[LINK](' + order_track + ')', inline = False)
                embed.set_thumbnail(url = product_image)
                embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
                webhook.add_embed(embed)
                response = webhook.execute()
        
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(order[0]))
            time.sleep(1)

        except KeyError:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(order[0]))
            failed_tracking += 1
        
        except Exception as e:
            print(str(e))
    
    webhook = DiscordWebhook(url = config['webhook_url'])
    embed = DiscordEmbed(title = 'Nike Tracking summary', color = 15815972)
    embed.add_embed_field(name = 'Overview:\n', value = '\n\U0001F3E2 Waiting for shipping: ' + str(order_awaiting_ship) + '\n\n\U0001F69A Package in transit: ' + str(order_shipped) + '\n\n\U0001F3E0 Delivered: ' + str(order_delivered) + '\n\n\U000026A0 Failed: ' + str(failed_tracking) + '\n\n\U0001F4DD Total: ' + str(failed_tracking + order_shipped + order_awaiting_ship + order_delivered), inline = False)
    embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
    webhook.add_embed(embed)
    response = webhook.execute()
    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Tracking finished")
    time.sleep(2)
    finish = input('Press Enter to continue...')
    return