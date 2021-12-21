from twilio.rest import Client
import requests
from requests_html import HTMLSession
import time
import datetime
import threading
import json
from threading import Timer

# Imports all config settings
with open('./config.json', 'r') as file:
    dictionary = json.load(file)

account_sid = dictionary['twilio_account_sid']
auth_token = dictionary['twilio_auth_token']
discord_webhook = dictionary['discord_webhook_url']
phone_numbers = dictionary['phone_numbers']
sender_phone_number = dictionary['sender_phone_number'],
delaySeconds= dictionary['delay_seconds']

print(account_sid)
# Gets all the files and prep variables
session = HTMLSession()

best_buy_urls = ['https://www.bestbuy.com/site/nvidia-geforce-rtx-3070-8gb-gddr6-pci-express-4-0-graphics-card-dark-platinum-and-black/6429442.p?skuId=6429442',
                 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3080-10gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429440.p?skuId=6429440',
                 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3060-ti-8gb-gddr6-pci-express-4-0-graphics-card-steel-and-black/6439402.p?skuId=6439402',
                 'https://www.bestbuy.com/site/nvidia-geforce-rtx-3090-24gb-gddr6x-pci-express-4-0-graphics-card-titanium-and-black/6429434.p?skuId=6429434',
                 "https://www.bestbuy.com/site/sony-playstation-5-console/6426149.p?skuId=6426149",
                 "https://www.bestbuy.com/site/sony-playstation-5-digital-edition-console/6430161.p?skuId=6430161",
                 "https://www.bestbuy.com/site/microsoft-xbox-series-x-1tb-console-black/6428324.p?skuId=6428324",]
                 
requests.post(discord_webhook,
            data={'content': 'GPU Checker has started'})


client = Client(account_sid, auth_token)

def sendMessage(bodyMessage):
    for phone in phone_numbers:
        message = client.messages \
                        .create(
                            body=bodyMessage,
                            from_=sender_phone_number,
                            to=phone
                        )
    return("Done")

def addBackToUrl(url):
    best_buy_urls.append(url)
# Keep checking
while True:

    # Displays current time and time until next update
    timeNow = datetime.datetime.now()
    delayTime = timeNow + datetime.timedelta(seconds=delaySeconds)
    print("\033[1;35;40m Another update in {} seconds! \033[1;34;40m Time Now: ".format(delaySeconds) +
          str(time.strftime("%H:%M:%S on %a, %b %d")) + "\033[0;37;40m\n")
    print("\033[1;35;40m Next update is at:  \033[1;34;40m" +
          str(delayTime.time())[:-7] + "\033[0;37;40m\n")
    time.sleep(delaySeconds)

    # Check all urls from bestbuyURL.txt
    for url in best_buy_urls:
        url = url.replace('\n', "")
        # Tries to search for the url
        try:
            bb = session.get(url)
        except ConnectionError:
            print("\033[2;31;40m CONNECTION ERROR! with " + url + " \033[0;37;40m\n")
            continue
        except Exception:
            print("\033[2;31;40m ERROR! " + str(Exception) +
                  " WITH URL " + str(url) + " \033[0;37;40m\n")
            continue
        # If url is found and can be opened, then check for the item name and the purchase button
        try:
            item_name = bb.html.find('.sku-title h1', first=True).text
        except Exception:
            item_name = "NOT FOUND"
            print("\033[2;31;40m COULD NOT FIND THE ITEM NAME")
            print("ERROR: " + str(Exception) + "\033[0;37;40m\n")
        try:
            checkInStock = bb.html.find(
                '.fulfillment-add-to-cart-button div button', first=True).attrs
            checkInstock = list(checkInStock.keys())
        except Exception:
            print("\033[2;31;40m COULD NOT CHECK STOCK STATUS, SKIPPING")
            print("ERROR: " + str(Exception) +
                  " with " + url + "\033[0;37;40m\n")
            continue
        # disabled = html atribute for button meaning can't click
        # check to see if the button is 'disabled', if it is, then that means you can't buy it
        if 'disabled' in checkInStock:
            print(" [Best Buy] " + item_name + ": " +
                  '\033[2;31;40m OUT OF STOCK\033[0;37;40m\n')
        else:
            print((" [Best Buy] " + item_name + ": " +
                   '\033[2;32;40m IN STOCK\033[0;37;40m\n') * 10)
            sendMessage("[IN STOCK]: " + " from [Best Buy]")
            requests.post(discord_webhook, data={
                      'content': '@everyone GPU IN STOCK: ' + url})
            best_buy_urls.remove(url)
            timer = Timer(60 * 30, addBackToUrl, args=[url])
            timer.start()
        if (datetime.datetime.now().hour > 13 or datetime.datetime.now().hour < 9):
            print("\033[1;35;40m Sleeping for 1 hour")
            time.sleep(60 * 60 * 1)
