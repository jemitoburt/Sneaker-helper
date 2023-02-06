from csv import DictReader
import os, requests, json, time, imaplib, email, quopri, re, base64, csv
from discord_webhook import DiscordWebhook, DiscordEmbed
from datetime import datetime
from bs4 import BeautifulSoup
import dateutil.parser as dp

path = os.getcwd()
files = os.listdir(path)

def carrier_tracking():
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)

    dpd_tracking_links = []
    ups_tracking_links = []
    chronopost_tracking_links = []
    dhl_tracking_links = []
    brt_tracking_links = []

    with open(path + '/carrier_tracker.csv', 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        carrier_index = header.index('CARRIER')
        tracking_number_index = header.index('TRACKING_NUMBER')
        
        for row in reader:
            carrier = row[carrier_index]
            tracking_number = row[tracking_number_index]
            
            if carrier == 'DPD':
                dpd_tracking_links.append(tracking_number)
            
            elif carrier == 'UPS':
                ups_tracking_links.append(tracking_number)
            
            elif carrier == 'CNP':
                chronopost_tracking_links.append(tracking_number)
            
            elif carrier == 'DHL':
                dhl_tracking_links.append(tracking_number)
            
            elif carrier == 'BRT':
                brt_tracking_links.append(tracking_number)

    os.system('title "Nike helper | Tracking {} orders"'.format(str(len(dpd_tracking_links + ups_tracking_links + chronopost_tracking_links + dhl_tracking_links))))

    dpd_status_accepted = 0
    dpd_status_in_transit = 0
    dpd_status_at_delivery_depot = 0
    dpd_status_out_for_delivery = 0
    dpd_status_delivered = 0
    dpd_failed_tracking = 0

    ups_status_accepted = 0
    ups_status_in_transit = 0
    ups_status_out_for_delivery = 0
    ups_status_delivered = 0
    ups_failed_tracking = 0

    dhl_status_accepted = 0
    dhl_status_in_transit = 0
    dhl_status_delivered = 0
    dhl_failed_tracking = 0

    chronopost_status_accepted = 0
    chronopost_status_in_transit = 0
    chronopost_status_out_for_delivery = 0
    chronopost_status_delivered = 0
    chronopost_failed_tracking = 0

    for link in dpd_tracking_links:
        json_data = open(path + '/config.json').read()
        config = json.loads(json_data)

        headers = {
            'Host': 'tracking.dpd.de',
            'Accept': 'application/json, text/plain, */*',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
            'Accept-Language': 'cs-CZ,cs;q=0.9',
            'Referer': 'https://tracking.dpd.de/status/cs_CZ/parcel/{}'.format(link),
        }
        try:
            response = json.loads(requests.get('https://tracking.dpd.de/rest/plc/cs_CZ/{}'.format(link), headers=headers).text)['parcellifecycleResponse']['parcelLifeCycleData']
            status_count = len(response['statusInfo'])
            status = response['statusInfo'][int(status_count) - 1]['status']
            if status == 'ACCEPTED':
                dpd_status_accepted += 1
            elif status == 'ON_THE_ROAD':
                dpd_status_in_transit += 1
            
            elif status == 'AT_DELIVERY_DEPOT':
                dpd_status_at_delivery_depot += 1
            
            elif status == 'OUT_FOR_DELIVERY':
                dpd_status_out_for_delivery += 1
            
            elif status == 'DELIVERED':
                dpd_status_delivered += 1
                
            last_location = response['statusInfo'][int(status_count) - 1]['location']
            last_scan_count = len(response['scanInfo']['scan'])
            last_scan = '<t:' +  str(dp.parse(response['scanInfo']['scan'][int(last_scan_count) - 1]['integrationDate']).timestamp()).split('.')[0] + '>'

            webhook = DiscordWebhook(url = config['webhook_url'])
            embed = DiscordEmbed(title = 'DPD Order - ' + status, color = 15815972, url = 'https://tracking.dpd.de/status/cs_CZ/parcel/{}'.format(link))
            embed.add_embed_field(name = 'Order number', value = '||' + link + '||', inline = False)
            embed.add_embed_field(name = 'Last location', value = last_location, inline = False)
            embed.add_embed_field(name = 'Last update', value = last_scan, inline = False)
            embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(link))
            time.sleep(1)
        
        except:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track {}".format(link))
            dpd_failed_tracking += 1
    
    for link in ups_tracking_links:
        json_data = open(path + '/config.json').read()
        config = json.loads(json_data)
        headers = {
            'Host': 'www.ups.com',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
            'accept-language': 'cs-CZ,cs;q=0.9',
        }

        params = {
            'loc': 'cs_CZ',
            'Requester': 'SBN',
            'tracknum': link,
            'AgreeToTermsAndConditions': 'yes',
        }

        response = requests.get('https://www.ups.com/track', params=params, headers=headers)

        csrf_token = response.cookies.get_dict().get("X-CSRF-TOKEN")
        csrf_token_2 = response.cookies.get_dict().get("X-XSRF-TOKEN-ST")

        cookies = {
            'X-CSRF-TOKEN': csrf_token,
            'ups_language_preference': 'cs_CZ',
        }

        headers = {
            'Host': 'www.ups.com',
            'content-type': 'application/json',
            'accept': 'application/json, text/plain, */*',
            'x-xsrf-token': csrf_token_2,
            'accept-language': 'cs-CZ,cs;q=0.9',
            'origin': 'https://www.ups.com',
            'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
            'referer': 'https://www.ups.com/track?loc=cs_CZ&Requester=SBN&tracknum={}&AgreeToTermsAndConditions=yes/trackdetails'.format(link),
        }

        params = {
            'loc': 'cs_CZ',
        }

        json_data = {
            'Locale': 'cs_CZ',
            'TrackingNumber': [
                link,
            ],
            'Requester': 'sbn',
            'returnToValue': '',
        }
        try:
            response = json.loads(requests.post('https://www.ups.com/track/api/Track/GetStatus',params=params,headers=headers,json=json_data,cookies=cookies).text)['trackDetails'][0]

            delivery_date = str(response['shipmentProgressActivities'][0]['date']) + ' ' + str(response['shipmentProgressActivities'][0]['time'])
            status = response['shipmentProgressActivities'][0]['milestoneName']['name']
            if status == 'Label Created':
                ups_status_accepted += 1
            elif status == 'On the Way':
                ups_status_in_transit += 1
            elif status == 'Out for Delivery':
                ups_status_out_for_delivery += 1
            elif status == 'Delivered':
                ups_status_delivered += 1
            last_location = response['shipmentProgressActivities'][0]['location']

            date_time_obj = datetime.strptime(delivery_date, "%d.%m.%Y %H:%M")
            timestamp = str(date_time_obj.timestamp()).split('.')[0]

            webhook = DiscordWebhook(url = config['webhook_url'])
            embed = DiscordEmbed(title = 'UPS Order - ' + status.upper(), color = 15815972, url = 'https://www.ups.com/track?loc=cs_CZ&Requester=SBN&tracknum={}&AgreeToTermsAndConditions=yes/trackdetails'.format(link))
            embed.add_embed_field(name = 'Order number', value = '||' + link + '||', inline = False)
            embed.add_embed_field(name = 'Last location', value = last_location, inline = False)
            embed.add_embed_field(name = 'Last update', value = '<t:' + str(timestamp) + '>', inline = False)
            embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            webhook.add_embed(embed)
            response = webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(link))
            time.sleep(1)
        
        except:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(link))
            ups_failed_tracking += 1
        
    for link in chronopost_tracking_links:
        json_data = open(path + '/config.json').read()
        config = json.loads(json_data)
        headers = {
            'Accept': 'application/json',
            'X-Forwarded-For': '123.123.123.123',
            'X-Okapi-Key': str(config['chronopost_api_key']),
        }

        params = {
            'lang': 'en_GB',
        }

        response = requests.get('https://api.laposte.fr/suivi/v2/idships/{}'.format(link), params=params, headers=headers)
        if response.status_code == 404:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(link))
            chronopost_failed_tracking += 1
        
        json_data = json.loads(response.text)
        try:
            status = json_data['shipment']['event'][0]['label']
            timestamp = json_data['shipment']['event'][0]['date']
            time_obj = datetime.strptime(timestamp, '%Y-%m-%dT%H:%M:%S%z')
            timestamp = str(time_obj.timestamp()).split('.')[0]
            if status == "Shipment in preparation to be shipped":
                chronopost_status_accepted += 1
                embed_status = 'WAITING FOR SHIPPING'
            if status == "Under preparation at the shipper's":
                chronopost_status_accepted += 1
                embed_status = 'WAITING FOR SHIPPING'
            if status == "Shipment in transit":
                chronopost_status_in_transit += 1
                embed_status = 'IN TRANSIT'
            if status == "Out for delivery":
                chronopost_status_out_for_delivery += 1
                embed_status = 'OUT FOR DELIVERY'
            if status == "Delivered":
                chronopost_status_delivered += 1
                embed_status = 'DELIVERED'

            chronopost_webhook = DiscordWebhook(url = config['webhook_url'])
            chronopost_embed = DiscordEmbed(title = 'Chronopost Order - {}'.format(embed_status), color = 15815972, url = 'https://www.laposte.fr/outils/suivre-vos-envois?code={}'.format(link))
            chronopost_embed.add_embed_field(name = 'Order number', value = '||' + link + '||', inline = False)
            chronopost_embed.add_embed_field(name = 'Last update', value = '<t:' + str(timestamp) + '>', inline = False)
            chronopost_embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            chronopost_webhook.add_embed(chronopost_embed)
            chronopost_embed_response = chronopost_webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(link))
            continue

        except:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(link))
            chronopost_failed_tracking += 1

    for link in dhl_tracking_links:
        json_data = open(path + '/config.json').read()
        config = json.loads(json_data)
        headers = {
            'DHL-API-Key': str(config['dhl_api_key']),
        }

        params = {
            'trackingNumber': str(link),
        }

        response = requests.get('https://api-eu.dhl.com/track/shipments', params=params, headers=headers)
        if response.status_code == 404:
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Failed to track order {}".format(link))
            dhl_failed_tracking += 1
        
        json_data = json.loads(response.text)
        try:
            status = json_data['shipments'][0]['status']['statusCode']
            if status == 'pre-transit':
                dhl_status_accepted += 1
                embed_status = 'WAITING FOR SHIPPING'
            
            if status == 'transit':
                dhl_status_in_transit += 1
                embed_status = 'IN TRANSIT'

            if status == 'delivered':
                dhl_status_delivered += 1
                embed_status = 'DELIVERED'

            tracking_number = json_data['shipments'][0]['id']
            last_location = json_data['shipments'][0]['events'][0]['location']['address']['addressLocality']
            last_scan = json_data['shipments'][0]['events'][0]['timestamp']
            timestamp = str(datetime.strptime(last_scan, '%Y-%m-%dT%H:%M:%S').timestamp()).split('.')[0]

            dhl_webhook = DiscordWebhook(url = config['webhook_url'])
            dhl_embed = DiscordEmbed(title = 'DHL Order - {}'.format(embed_status), color = 15815972, url = 'https://www.dhl.com/en/express/tracking.html?AWB={}&brand=DHL'.format(link))
            dhl_embed.add_embed_field(name = 'Order number', value = '||' + tracking_number + '||', inline = False)
            dhl_embed.add_embed_field(name = 'Last location', value = last_location, inline = False)
            dhl_embed.add_embed_field(name = 'Last update', value = '<t:' + str(timestamp) + '>', inline = False)
            dhl_embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            dhl_webhook.add_embed(dhl_embed)
            dhl_embed_response = dhl_webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(link))

        except KeyError:
            dhl_webhook = DiscordWebhook(url = config['webhook_url'])
            dhl_embed = DiscordEmbed(title = 'DHL Order - WAITING FOR SHIPPING', color = 15815972, url = 'https://www.dhl.com/en/express/tracking.html?AWB={}&brand=DHL'.format(link))
            dhl_embed.add_embed_field(name = 'Order number', value = '||' + link + '||', inline = False)
            dhl_embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
            dhl_webhook.add_embed(dhl_embed)
            dhl_embed_response = dhl_webhook.execute()
            print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Found order {}".format(link))
            dhl_status_accepted += 1

    ups_total = ups_status_out_for_delivery + ups_status_delivered + ups_failed_tracking + ups_status_in_transit + ups_status_accepted
    dhl_total = dhl_status_in_transit + dhl_status_delivered + dhl_failed_tracking + dhl_status_accepted
    dpd_total = dpd_status_accepted + dpd_status_in_transit + dpd_status_at_delivery_depot + dpd_status_out_for_delivery + dpd_status_delivered + dpd_failed_tracking
    chronopost_total = chronopost_status_out_for_delivery + chronopost_status_delivered + chronopost_failed_tracking + chronopost_status_accepted + chronopost_status_in_transit
    
    webhook = DiscordWebhook(url = config['webhook_url'])
    embed = DiscordEmbed(title = 'Tracking summary', color = 15815972)
    if dpd_total != 0:
        embed.add_embed_field(name = 'Overview DPD:\n', value = '\n\U0001F3E2 Waiting for shipping: ' + str(dpd_status_accepted) + '\n\n\U0001F69A Package in transit: ' + str(dpd_status_in_transit) + '\n\n\U0001F3EC Delivery warehouse: ' + str(dpd_status_at_delivery_depot) + '\n\n\U0001F69A Out for delivery: ' + str(dpd_status_out_for_delivery) + '\n\n\U0001F3E0 Delivered: ' + str(dpd_status_delivered) + '\n\n\U000026A0 Failed: ' + str(dpd_failed_tracking) + '\n\n\U0001F4DD Total: ' + str(dpd_total), inline = True)
    if ups_total != 0:
        embed.add_embed_field(name = 'Overview UPS:\n', value = '\n\U0001F3E2 Waiting for shipping: ' + str(ups_status_accepted) + '\n\n\U0001F69A Package in transit: ' + str(ups_status_in_transit) + '\n\n\U0001F69A Out for delivery: ' + str(ups_status_out_for_delivery) + '\n\n\U0001F3E0 Delivered: ' + str(ups_status_delivered) + '\n\n\U000026A0 Failed: ' + str(ups_failed_tracking) + '\n\n\U0001F4DD Total: ' + str(ups_total), inline = True)
    if dhl_total != 0:
        embed.add_embed_field(name = 'Overview DHL:\n', value = '\n\U0001F3E2 Waiting for shipping: ' + str(dhl_status_accepted) + '\n\n\U0001F69A Package in transit: ' + str(dhl_status_in_transit) + '\n\n\U0001F3E0 Delivered: ' + str(dhl_status_delivered) + '\n\n\U000026A0 Failed: ' + str(dhl_failed_tracking) + '\n\n\U0001F4DD Total: ' + str(dhl_total), inline = True)
    if chronopost_total != 0:
        embed.add_embed_field(name = 'Overview Chronopost:\n', value = '\n\U0001F3E2 Waiting for shipping: ' + str(chronopost_status_accepted) + '\n\n\U0001F69A Package in transit: ' + str(chronopost_status_in_transit) + '\n\n\U0001F69A Out for delivery: ' + str(chronopost_status_out_for_delivery) + '\n\n\U0001F3E0 Delivered: ' + str(chronopost_status_delivered) + '\n\n\U000026A0 Failed: ' + str(chronopost_failed_tracking) + '\n\n\U0001F4DD Total: ' + str(chronopost_total), inline = True)
    embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()), icon_url = 'https://i.imgur.com/Xln1cg7.png')
    webhook.add_embed(embed)
    response = webhook.execute()
    print(datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Tracking finished")
    time.sleep(2)
    finish = input('Press Enter to continue...')
    return