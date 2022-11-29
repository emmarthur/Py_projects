# -*- coding: utf-8 -*-
"""
Created on Sat Nov 19 02:26:57 2022

@author: earthur
"""
import smtplib, ssl
import requests
import lxml.html

#Open up web page
html = requests.get('https://store.steampowered.com/explore/new/') 

#Pass the web page content to lxml
doc = lxml.html.fromstring(html.content)

#write and store an XPath for extracting the div which contains the ‘Popular New Releases’
new_releases = doc.xpath('//div[@id="tab_newreleases_content"]')[0]

# query the Xpath for titles and store the responses
titles = new_releases.xpath('.//div[@class="tab_item_name"]/text()')

# query the Xpath for discounted prices and store the responses  
prices = new_releases.xpath('.//div[@class="discount_final_price"]/text()')

#Extract all tags from the Xpath
tags = []
for tag in new_releases.xpath('.//div[@class="tab_item_top_tags"]'): 
    tags.append(tag.text_content())
tags = [tag.split(', ') for tag in tags]

#Extract the divs with the tab_item_details class and store them
platforms_div = new_releases.xpath('.//div[@class="tab_item_details"]') 

#extract the spans containing the platform_img class 
#and finally extract the second class name from those spans
total_platforms = []
for game in platforms_div:
    temp = game.xpath('.//span[contains(@class, "platform_img")]')
    print("temp = ", temp)
    platforms = [t.get('class').split(' ')[-1] for t in temp]
    print("platforms = ", platforms)
    if 'hmd_separator' in platforms:
        platforms.remove('hmd_separator') 
    total_platforms.append(platforms)
    
#Create dictionaries for titles, prices, tags, and platforms and store those dictionaries 
output = []
for info in zip(titles,prices, tags, total_platforms): 
    resp = {}
    resp['title'] = info[0] 
    resp['price'] = info[1] 
    resp['tags'] = info[2]
    resp['platforms'] = info[3] 
    output.append(resp)

#Get all free games and strategy games
all_free = list(filter(lambda a:a['price'] == 'Free to Play', output))
all_strategy = list(filter(lambda a:'Strategy' in a['tags'], output))

all_free_titles = [str(i+1)+". "+dic['title'] for i,dic in enumerate(all_free)]
all_strategy = [str(i+1)+". "+dic['title'] for i,dic in enumerate(all_strategy)]

#Send Game Info from one email address to another
port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "sender@gmail.com"  # Enter your address
receiver_email = "receiver@gmail.com"  # Enter receiver address
password = input("Type your password and press enter: ")
message = """n
Subject: Here are your free and strategy games
Free games: \n {} \n
Strategy games: \n {} \n
This message is sent from Python."""
message = message.format("\n".join(all_free_titles),"\n".join(all_strategy))

context = ssl.create_default_context()
with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, message)
