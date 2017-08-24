#!/usr/bin/env python

#
# Quick and dirty script to notify me when a new Macbook with 16GB of RAM and an i7 processor gets listed in the outlet store.
# Uses a flat file in same directory for persistent data store that gets checked and pruned on every run.  Fancy, huh?
# Ran and tested on python 3.5.2
#

import requests
from bs4 import BeautifulSoup
import re
from twilio.rest import Client

twilio = Client('<TWILIO_ACCOUNT>', '<TWILIO_TOKEN>')
f = open('macbooks', 'r+', encoding='utf-8')
macbooks = list()

known_macbooks = list()
for macbook in f:
    known_macbooks.append(macbook.strip('\n'))

f.close()
f = open('macbooks', 'w', encoding='utf-8')

content = requests.get('https://www.apple.com/shop/browse/home/specialdeals/mac/macbook_pro/13').text
content_soup = BeautifulSoup(content)
products = content_soup.find_all('tr', class_='product')

for product in products:
    product_specs = product.find_all('td', class_='specs')
    ram = re.search("16GB", product_specs[0].get_text()) 
    processor = re.search("Intel (i7|Core i7)", product_specs[0].get_text())

    if ram and processor:
        price = product.find_all('span', itemprop='price')[0].get_text().rstrip().lstrip()
        link = 'https://www.apple.com' + product_specs[0].a.get('href')
        if known_macbooks.count(link) == 0:
            macbooks.append((price, link))
            f.write(link + "\n")
f.close()

if len(macbooks) > 0:
    sms_body = "Macbook(s) with i7 processor and 16GB of RAM listed: \n"
    for macbook in macbooks:
        sms_body += macbook[0] + ' -- ' + macbook[1] + "\n"
    sms = twilio.messages.create(to='<TWILIO_TO>', from_='<TWILIO_FROM>', body=sms_body)
