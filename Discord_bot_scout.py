import discord
from datetime import datetime
import csv

client = discord.Client()

@client.event
async def on_ready():
    print("Ready")

def size_convert(size, size_gender):
    if size_gender == "Femme":
        size_chart = {
            "35.5": "5W",
            "36": "5.5W",
            "36.5": "6W",
            "37.5": "6.5W",
            "38": "7W",
            "38.5": "7.5W",
            "39": "8W",
            "40": "8.5W",
            "40.5": "9W",
            "41": "9.5W",
            "42": "10W",
            "42.5": "10.5W",
            "43": "11W",
            "44": "11.5W",
            "44.5": "12W"
        }
        size_converted = size_chart[size]
        return size_converted
    
    if size_gender == "Homme":
        size_chart = {
            "38.5": "6",
            "39": "6.5",
            "40": "7",
            "40.5": "7.5",
            "41": "8",
            "42": "8.5",
            "42.5": "9",
            "43": "9.5",
            "44": "10",
            "44.5": "10.5",
            "45": "11",
            "45.5": "11.5",
            "46": "12",
            "47": "12.5",
            "47.5": "13",
            "48": "13.5",
            "48.5": "14",
            "49.5": "15"
        }
        size_converted = size_chart[size]
        return size_converted
    
    if size_gender == "Enfant plus âgé":
        size_chart = {
            "35": "3.5Y",
            "36": "4Y",
            "36.5": "4.5Y",
            "37.5": "5Y",
            "38": "5.5Y",
            "38.5": "6Y",
            "39": "6.5Y",
            "40": "7Y"
        }
        size_converted = size_chart[size]
        return size_converted

def write_to_csv(store, size_converted, sku, order_id, date_string, product_name):
    export = open('Scout inventory tracker/scout_app_import.csv', 'a')
    export.write(product_name + "," + store + "," + sku + "," + "" + "," + size_converted + "," + order_id + "," + date_string + "\n")
    export.close()
    print('Added size to csv')

@client.event
async def on_message(message):
    if message.channel.name == "coding":
        bot = str(message.embeds[0].footer.text)
        if 'uSNKRS' in bot:
            store = 'Nike'
            sku = str(message.embeds[0].fields[3].value).split(" - ")[1]
            product_name = str(message.embeds[0].fields[3].value).split(" - ")[0].split(' ')[1]
            size_gender = str(message.embeds[0].fields[3].value).split(" - ")[0].split("pour ")[1]
            size = str(message.embeds[0].fields[2].value).split(" ")[1].split(" ")[0]
            order_id = str(message.embeds[0].fields[5].value)
            size_converted = size_convert(size, size_gender)
            #date_string = datetime.today().strftime("%d.%m.%Y")
            date_string = datetime.today().strftime("%m.%d.%Y")
            write_to_csv(store, size_converted, sku, order_id, date_string, product_name)

client.run("MTA1MzMwMDgyMDExODA4MTU1Ng.G0CuO3.QXnm0PH3lYQzecpClhOAQnCGyo30uFSsHHvFrM")