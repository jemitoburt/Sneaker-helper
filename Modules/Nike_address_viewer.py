import os, requests, json, time, imaplib, email, quopri, re, base64, csv
from discord_webhook import DiscordWebhook, DiscordEmbed
from csv import DictReader
from datetime import datetime

path = os.getcwd()
files = os.listdir(path)

def read_csv_nike_address_viewer():
    track_data = []
    order_count = 0
    with open(path + '/address_viewer.csv') as f:
        reader = DictReader(f)
        for line in reader:
            order_number = line['ORDER_NUMBER']
            order_email = line['ORDER_EMAIL']
            track_data.append([order_number, order_email])
            order_count += 1
    os.system('title "Nike helper | Searching for ' + str(order_count) + ' addresses')
    return track_data

def write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number):
    export = open(path + '/address_viewer_export.csv', 'a')
    export.write(delivery_name + "," + delivery_street + "," + delivery_city + "," + carrier + "," + tracking_number + "\n")
    export.close()
    time.sleep(1)

def scrape_delivery_address(track_data):
    json_data = open(path + 'config.json').read()
    config = json.loads(json_data)
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
            response_json = json.loads(requests.get('https://api.nike.com/orders/summary/v1/' + order[0], params=params, headers=headers).text)
            address = response_json['shippingAddress']
            delivery_name = address[0]
            delivery_street = address[1]
            delivery_city = address[3]

            try:
                order_track = response_json['group'][0]['actions']['trackShipment']['webLink']
                if 'UPS' in order_track:
                    carrier = 'UPS'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
                
                if 'DPD' in order_track:
                    carrier = 'DPD'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
                
                if 'POST' in order_track:
                    carrier = 'POST_NL'
                    zip_code = response_json['shipFrom']['address']['zipCode']
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
                
                if 'CNP' in order_track:
                    carrier = 'CHRONOPOST'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
                
                if 'DHL' in order_track:
                    carrier = 'DHL'
                    zip_code = response_json['shipFrom']['address']['zipCode']
                    try:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
                
                if 'BRT' in order_track:
                    carrier = 'BRT'
                    zip_code = ''
                    try:
                        tracking_number = str(order_track).split('tracking_numbers=')[1].split('&')[0]
                    except:
                        tracking_number = str(order_track).split('tracking_number=')[1].split('&')[0]
                    write_address(delivery_name, delivery_street, delivery_city, carrier, tracking_number)
            
            except KeyError:
                order_track = 'Tracking link not found'
            
            except Exception as e:
                print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}\n Error: {}".format(order[0], str(e)))
                
            webhook = DiscordWebhook(url = config['webhook_url'])
            embed = DiscordEmbed(title = 'Found address', color = 15815972)
            embed.add_embed_field(name = 'Order number', value = '||' + order[0] + '||', inline = False)
            embed.add_embed_field(name = 'Address', value = address[1] + '\n' + address[3], inline = False)
            embed.add_embed_field(name = 'Order tracking', value = '[LINK](' + order_track + ')', inline = False)
            embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(order[0]))

        except KeyError:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(order[0]))
        
        except Exception as e:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}\n Error: {}".format(order[0], str(e)))
    
    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Sended all addresses")
    time.sleep(2)
    finish = input('Press Enter to continue...')
    return