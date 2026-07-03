from bs4 import BeautifulSoup
import requests
import time
import datetime
from discord_webhook import DiscordWebhook,DiscordEmbed
import os

datagbf={"Event":[],"Img":[],"Time":[],"Status":[],"TimeF":[]}

sentlogs="./logs/content.log"
errlogs="./logs/err.log"
if not os.path.exists(sentlogs):
  with open(sentlogs,"w") as ff:
    pass
if not os.path.exists(errlogs):
    with open(errlogs,"w") as ff:
        pass

try:
  hooklink=os.environ['HOOKSECRET']
  
except Exception as ee:
  with open(errlogs,"a+") as ff:
    err=f"{datetime.datetime.today()}||Err: {ee}\n"
    ff.write(err)
    exit()

try:
  with open(sentlogs,"+r") as ff:
    sentt=ff.readlines()
    entryno=len(sentt)
    
  url = requests.get('https://gbf.wiki/')
  soup = BeautifulSoup(url.text,features="html.parser")
  events_card = soup.find('div', class_='card card-current-events')
  if events_card:    
    seen_events = []
    banner_divs = events_card.find_all('div', class_=lambda c: c and 'event-banner__image' in c)
    for banner_div in banner_divs:
        a_tag = banner_div.find('a', title=True)
        if not a_tag:
            continue
        event_title = a_tag['title']

        img_tag = banner_div.find('img')
        image_url = img_tag['src'] if img_tag else "https://i.imgur.com/eOtuYwq.png"
        
        #print(f"\nEvent: {event_title}")
        #print(f"Banner: {image_url}")

        if 'event-banner__image--has-ended' in banner_div.get('class', []):
          
            timeff=banner_div.find_next('span', class_='localtime').text.strip()
            chk2=f"{event_title}|{timeff}|Ended\n"
            if chk2 in sentt:
              continue
            
            datagbf["Event"].append(event_title)
            datagbf["Img"].append(image_url)
            datagbf["TimeF"].append(timeff)
            datagbf["Time"].append("Event has already ended.")
            datagbf["Status"].append("Ended")
        else:

            time_tag = banner_div.find_next('span', class_='localtime')
            timeff=time_tag.text.strip()
            span_text = time_tag.get_text(strip=True) if time_tag else "No tag found"
            if time_tag and time_tag.get('data-text-end') == "Ends in":
                end_timestamp = int(time_tag.get('data-end'))
                current_timestamp = int(time.time())
                seconds_remaining = end_timestamp - current_timestamp
                hours_left = round(seconds_remaining / 3600, 1)
                if 0 < seconds_remaining < (10 * 3600):
                    
                    chk2=f"{event_title}|{timeff}|Alert\n"
                    if chk2 in sentt:
                       continue
                    datagbf["Time"].append("Lock in, chat! Only {hours_left} hours remaining!")
                    datagbf["Status"].append("Alert")
                else:
                  chk2=f"{event_title}|{timeff}|Active\n"
                  if chk2 in sentt:
                       continue
                  days = seconds_remaining // 86400  
                  hours = (seconds_remaining % 86400) // 3600
                  
                  aaa=f"Ends in {days}d {hours}h"
                  datagbf["Time"].append(aaa)
                  datagbf["Status"].append("Active")
            else:
                chk2=f"{event_title}|{timeff}|Active\n"
                if chk2 in sentt:
                  continue
                datagbf["Time"].append("Status: Active")
                datagbf["Status"].append("Active")    
            
            datagbf["Event"].append(event_title)
            datagbf["Img"].append(image_url)
            datagbf["TimeF"].append(timeff)             
                
        seen_events.append(event_title)
  a=0
  for eventss in datagbf["Event"]:
    name,img,time,timef,stat=eventss,datagbf["Img"][a],datagbf["Time"][a],datagbf["Status"][a],datagbf["TimeF"][a]
    chk=f"{name}|{stat}|{timef}\n"
    if entryno>40:
       with open(sentlogs,"w") as ff:
        newlog=''.join(sentt[100:])
        ff.write(newlog)
       with open(errlogs,"w") as ff:
        pass
    with open(sentlogs,"a+") as ff:
        ff.write(chk)
    webhook=DiscordWebhook(url=hooklink)
    embed = DiscordEmbed(title=f'**{name} <:Ferrywhoaaaa:1522695828261568583>**',color=0x798db4)
    embed.set_image(url=f"{img}")
    embed.set_footer(text=f"{time}")
    webhook.add_embed(embed)
    webhook.execute()
    a+=1

except Exception as e:
  with open(errlogs,"a+") as ff:
    err=f"{datetime.datetime.today()}||FeedErr: {e}\n"
    ff.write(err)
