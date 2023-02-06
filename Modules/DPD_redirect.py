import time, requests, json, os
from datetime import datetime
from csv import DictReader
from discord_webhook import DiscordWebhook, DiscordEmbed

success_redirects = 0
failed_redirects = 0


""" parcel_number = '05308114709128'
parcel_code = '3457'
delivery_date = '26.04.2002'
email = ''
phone = '733295149'
zip = '72525'
city = 'Ostrava'
house_number = '1273'
street = 'Nabrezni'
name = 'Marek Syvala' """

tasks = []

def read_tasks():
    path = os.getcwd()
    with open (path + "/dpd_redirect.csv", 'r') as read_obj:
        csv_dict_reader = DictReader(read_obj)
        for row in csv_dict_reader:
            tasks.append(row)

def format_time(delivery_date):
    formatted_date = datetime.strptime(delivery_date, "%d.%m.%Y").strftime("%Y%m%d")
    return formatted_date

def send_webhook(parcel_number, delivery_date):
    path = os.getcwd()
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    webhook = DiscordWebhook(url = config['webhook_url'])
    embed = DiscordEmbed(title = 'Succesfully redirected', color = 000000)
    embed.add_embed_field(name = 'Order number', value = '||' + parcel_number + '||', inline = False)
    embed.add_embed_field(name = 'Delivery date', value = delivery_date, inline = False)
    embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()))
    webhook.add_embed(embed)
    response = webhook.execute()

def send_webhook_summary():
    path = os.getcwd()
    json_data = open(path + '/config.json').read()
    config = json.loads(json_data)
    webhook = DiscordWebhook(url = config['webhook_url'])
    embed = DiscordEmbed(title = 'Redirect summary', color = 000000)
    embed.add_embed_field(name = 'Overview:\n', value = '\U0001F64C Successfully redirect: ' + str(success_redirects) + ' parcels\n\n\U0000274C Failed to redirect: ' + str(failed_redirects) + ' parcels\n\n\U0001F4DD Total: ' + str(len(tasks)) + ' parcels', inline = False)
    embed.set_footer(text='Nike helper \U000000B7 ' + str(datetime.now()))
    webhook.add_embed(embed)
    response = webhook.execute()

def get_csv_data(task):
    parcel_number = task['PARCEL_NUMBER']
    parcel_code = task['PARCEL_CODE']
    delivery_date = task['DELIVERY_DATE']
    email = task['EMAIL']
    phone = task['PHONE']
    zip = task['ZIP']
    city = task['CITY']
    house_number = task['HOUSE_NUMBER']
    street = task['STREET']
    name = task['NAME']

    return parcel_number, parcel_code, delivery_date, email, phone, zip, city, house_number, street, name

def get_cookies():
    headers = {
        'Host': 'dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        # 'Cookie': f'dtCookie=v_4_srv_5_sn_DC965BB1C66C2C2D9C4BC12A9E46A326_perc_100000_ol_0_mul_1_app-3Ae2e0fb8733e43c8f_0; dtSa=-; rxVisitor=167172954577895KR1QGQD94GTD40BMIDI43R4FQ6KCQQ; _fbp=fb.1.1671729546868.431873975; dtPC=5{129545777_810h-vBATLHFUGAROHURKUIGTSKAKTAMSREMHB-0e0;} rxvt=1671731347179|1671729545779; _ga=GA1.2.1061964380.1671729546; _gat=1; _gcl_au=1.1.808029512.1671729547; _gid=GA1.2.563625996.1671729546; dtLatC=17; DPDKuryr_SessionState=hjuce0ezk2m12dpla5z2o2zk; __RequestVerificationToken=FfRofyc1rFxiFCQX1t3HKftX1005M1mgUjiQ8jWjcf-vrIDgG8EbHLjcdQHxPJ9iFUZncgvQh4mG2xeF9Rf3qV6tn2NYKpu1LMgoGE9SVtM1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
    }

    params = {
        'utm_source': 'notifikace',
        'utm_medium': 'e-mail',
        'utm_content': 'ofd',
        'utm_campaign': 'DPD_Kuryr',
    }

    response = requests.get('https://dpdkuryr.cz/Home/Parcel', params=params, headers=headers)
    verification_token = response.text.split('__RequestVerificationToken')[1].split('" />')[0].split('value="')[1]
    verification_cookies = response.cookies
    print('Got cookies and token')
    time.sleep(1)
    return verification_token, verification_cookies

def login(verification_token, verification_cookies, parcel_number, parcel_code):
    headers = {
        'Host': 'dpdkuryr.cz',
        'Origin': 'https://dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Referer': 'https://dpdkuryr.cz/Home/Parcel?utm_source=notifikace&utm_medium=e-mail&utm_content=ofd&utm_campaign=DPD_Kuryr',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
    }

    data = {
        '__RequestVerificationToken': verification_token,
        'Parcel': parcel_number,
        'PersonalCode': parcel_code,
    }

    response_main_page = requests.post('https://dpdkuryr.cz/Home/Parcel', cookies=verification_cookies, headers=headers, data=data)
    print('Successfully logged in')
    time.sleep(1)
    return

def get_address_page(verification_cookies, parcel_number):
    headers = {
        'Host': 'dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
        'Referer': 'https://dpdkuryr.cz/Home/Detail?parcel={}'.format(parcel_number),
    }

    params = {
        'parcel': parcel_number,
    }

    response = requests.get('https://dpdkuryr.cz/Home/ChangeAddress', params=params, cookies=verification_cookies, headers=headers)
    print('Got address page')
    time.sleep(1)
    return

def get_deliver_dates(parcel_number, verification_cookies, verification_token, name, zip, city, street, house_number, phone, email):
    headers = {
        'Host': 'dpdkuryr.cz',
        'Origin': 'https://dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Referer': 'https://dpdkuryr.cz/Home/ChangeAddress?parcel={}'.format(parcel_number),
        'Accept-Language': 'cs-CZ,cs;q=0.9',
    }

    data = {
        '__RequestVerificationToken': verification_token,
        'ParcelNumber': parcel_number,
        'Parcels': '',
        'Phase': 'EditAddress',
        'AddressType': 'Edit',
        'Name': str(name),
        'PostalCode': str(zip),
        'City': str(city),
        'Street': str(street),
        'HouseNumber': str(house_number),
        'Phone': str(phone),
        'Email': str(email),
        'SendInfoAgreement': 'false',
        'SendInfoEmail': str(email),
    }

    response_submit_address = requests.post('https://dpdkuryr.cz/Home/ChangeAddress', cookies=verification_cookies, headers=headers, data=data, allow_redirects=False)
    HiddenAvailableDates = response_submit_address.text.split('<input id="CommonPart_HiddenAvailableDates" name="CommonPart.HiddenAvailableDates" type="hidden"')[1].split('" />')[0].split('="')[1]
    HiddenAvailableDatesPaid = response_submit_address.text.split('<input id="CommonPart_HiddenAvailableDatesPaid" name="CommonPart.HiddenAvailableDatesPaid" type="hidden"')[1].split('" />')[0].split('="')[1]
    print('Got delivery dates')
    time.sleep(1)
    return HiddenAvailableDates, HiddenAvailableDatesPaid

def submit_date(parcel_number, verification_cookies, verification_token, HiddenAvailableDates, HiddenAvailableDatesPaid, name, zip, city, street, house_number, phone, email, formatted_date, delivery_date):
    headers = {
        'Host': 'dpdkuryr.cz',
        'Origin': 'https://dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Referer': 'https://dpdkuryr.cz/Home/ChangeAddress',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
    }

    data = {
        '__RequestVerificationToken': verification_token,
        'ParcelNumber': parcel_number,
        'Parcels': '',
        'Phase': 'ConfirmDate',
        'AddressType': 'Edit',
        'ConfirmedDate': str(formatted_date),
        'Street': str(street),
        'HouseNumber': str(house_number),
        'City': str(city),
        'PostalCode': str(zip),
        'Phone': str(phone),
        'Email': str(email),
        'SendInfoAgreement': 'false',
        'SendInfoEmail': str(email),
        'Name': str(name),
        'CommonPart.HiddenAvailableDates': str(HiddenAvailableDates),
        'CommonPart.HiddenAllowedDayParts': '',
        'CommonPart.HiddenDatesWithDayPartAvailable': str(HiddenAvailableDates),
        'CommonPart.HiddenDatesWithFixedDayPart': '',
        'CommonPart.HiddenAvailableDatesPaid': str(HiddenAvailableDatesPaid),
        'CommonPart.AllowSaturday': 'False',
        'CommonPart.DateSaturday': '',
        'CommonPart.AllowSunday': 'False',
        'CommonPart.DateSunday': '',
        'CommonPart.EditMode': 'W',
        'CommonPart.DeliveryDate': str(formatted_date),
        'CommonPart.DeliveryPart': '',
    }

    response = requests.post('https://dpdkuryr.cz/Home/ChangeAddress', cookies=verification_cookies, headers=headers, data=data, allow_redirects=False)
    print('Submitted address and date')
    time.sleep(1)
    if response.status_code == 302:
        print('Succesfully redirected order')
        send_webhook(parcel_number, delivery_date)
        success_redirects + 1
    
    else:
        print('Failed to redirect order')
        failed_redirects + 1

    return


def get_homepage(parcel_number, verification_cookies):
    headers = {
        'Host': 'dpdkuryr.cz',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        # 'Cookie': f'_fbp=fb.1.1671729546868.431873975; dtCookie=v_4_srv_5_sn_DC965BB1C66C2C2D9C4BC12A9E46A326_perc_100000_ol_0_mul_1_app-3Ae2e0fb8733e43c8f_0; dtSa=true%7CC%7C-1%7CUlo%C5%BEit%20zm%C4%9Bny%7C-%7C1671730612863%7C130608720_718%7Chttps%3A%2F%2Fdpdkuryr.cz%2FHome%2FChangeAddress%7C%7C%7C%7C; rxVisitor=167172954577895KR1QGQD94GTD40BMIDI43R4FQ6KCQQ; _ga=GA1.2.1061964380.1671729546; _gat=1; _gid=GA1.2.563625996.1671729546; dtPC=5{130608720_718h-vBATLHFUGAROHURKUIGTSKAKTAMSREMHB-0e0;} rxvt=1671732408937|1671729545779; dtLatC=1; _gcl_au=1.1.808029512.1671729547; DPDKuryr_SessionState=hjuce0ezk2m12dpla5z2o2zk; __RequestVerificationToken=FfRofyc1rFxiFCQX1t3HKftX1005M1mgUjiQ8jWjcf-vrIDgG8EbHLjcdQHxPJ9iFUZncgvQh4mG2xeF9Rf3qV6tn2NYKpu1LMgoGE9SVtM1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.2 Safari/605.1.15',
        'Accept-Language': 'cs-CZ,cs;q=0.9',
        'Referer': 'https://dpdkuryr.cz/Home/ChangeAddress',
    }

    params = {
        'parcel': parcel_number,
    }

    response = requests.get('https://dpdkuryr.cz/Home/Detail', params=params, cookies=verification_cookies, headers=headers)

def run(task):
    parcel_number, parcel_code, delivery_date, email, phone, zip, city, house_number, street, name = get_csv_data(task)
    verification_token, verification_cookies = get_cookies()
    login(verification_token, verification_cookies, parcel_number, parcel_code)
    get_address_page(verification_cookies, parcel_number)
    HiddenAvailableDates, HiddenAvailableDatesPaid = get_deliver_dates(parcel_number, verification_cookies, verification_token, name, zip, city, street, house_number, phone, email)
    formatted_date = format_time(delivery_date)
    submit_date(parcel_number, verification_cookies, verification_token, HiddenAvailableDates, HiddenAvailableDatesPaid, name, zip, city, street, house_number, phone, email, formatted_date, delivery_date)


def dpd_redirect():
    read_tasks()
    for task in tasks:
        run(task)
        time.sleep(5)
    send_webhook_summary()