import os, time, datetime
from colorama import Fore, init
from pypresence import Presence
from Modules.Discord_bot_live import discord_bot_live
from Modules.Discord_bot_past import discord_bot_past
from Modules.Nike_order_tracker import read_csv_nike_track, track_nike
from Modules.Gmail_scraper import gmail_dpd
from Modules.Carrier_tracker import carrier_tracking
from Modules.Key_verification import validate_key
from Modules.Nike_address_viewer import read_csv_nike_address_viewer, scrape_delivery_address

path = os.getcwd()
files = os.listdir(path)

init(convert=True)

banner = """
 _    _      _                            _          _   _ _ _          _          _                 
| |  | |    | |                          | |        | \ | (_) |        | |        | |                
| |  | | ___| | ___ ___  _ __ ___   ___  | |_ ___   |  \| |_| | _____  | |__   ___| |_ __   ___ _ __ 
| |/\| |/ _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \  | . ` | | |/ / _ \ | '_ \ / _ \ | '_ \ / _ \ '__|
\  /\  /  __/ | (_| (_) | | | | | |  __/ | || (_) | | |\  | |   <  __/ | | | |  __/ | |_) |  __/ |   
 \/  \/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/  \_| \_/_|_|\_\___| |_| |_|\___|_| .__/ \___|_|   
                                                                                    | |              
                                                                                    |_|              
"""

def clear():
    os.system('cls' if os.name=='nt' else 'clear')

def menu():
    print(Fore.RED + banner + Fore.RESET)
    try:
        user_rpc = Presence('1053300820118081556')
        user_rpc.connect()
        user_rpc.update(details='Helping with your Nike journey', large_image='presence_logo', start=time.time(), buttons=[{"label": "Twitter", "url": "https://twitter.com/nike_helper"}])
    except BaseException:
        pass
    os.system('title "Nike helper"')
    print('Which module do you want to start?\n1. Discord bot tracker - live\n2. Discord bot tracker - past\n3. Nike tracker\n4. Nike address viewer\n5. Nike order canceller\n6. Gmail scraper\n7. DPD Parcel redirect\n8. Carrier tracker\n9. Exit')
    module = int(input(datetime.datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Enter module number: "))
    if module == 1:
        discord_bot_live()
    
    if module == 2:
        count = str(input(datetime.datetime.now().strftime(f"[%H:%M:%S]") + " - " + "How many embeds do you want to scrape? "))
        discord_bot_past(count)
        clear()
        menu()

    if module == 3:
        track_data = read_csv_nike_track()
        track_nike(track_data)
        clear()
        menu()

    if module == 4:
        track_data = read_csv_nike_address_viewer()
        scrape_delivery_address(track_data)
        clear()
        menu()

    if module == 5:
        print('This module is not available yet, going back to menu...')
        time.sleep(2)
        clear()
        menu()
    
    if module == 6:
        gmail_dpd()
        clear()
        menu()

    if module == 7:
        print('This module is not available yet, going back to menu...')
        time.sleep(2)
        clear()
        menu()

    if module == 8:
        carrier_tracking()
        clear()
        menu()

    if module == 9:
        exit()

validation = validate_key()
if validation == True:
    menu()

elif validation == False:
    print(datetime.datetime.now().strftime(f"[%H:%M:%S]") + " - " + "Invalid key, please contact support")
    time.sleep(2)
    input('Press ENTER to exit')