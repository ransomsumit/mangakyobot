import os
import re
import time
import json
import telepot
import validators
import requests
from bs4 import BeautifulSoup as soup
from flask import Flask, request
from telepot.loop import MessageLoop
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton, InlineQueryResultArticle, InputTextMessageContent
from telepot.delegate import pave_event_space, per_chat_id, create_open, \
    include_callback_query_chat_id, per_inline_from_id


TOKEN= "1113817716:AAGjlPbMvLTBn-BIF5SFnujqDbQA0qVzgfo"

class Mangakyo(telepot.helper.InlineUserHandler, telepot.helper.AnswererMixin):
    def __init__(self, *args, **kwargs):
        super(Mangakyo, self).__init__(*args, **kwargs)
        self._count = 0

    def on_chat_message(self, msg):
        content_type, chat_type, chat_id = telepot.glance(msg)
        group_id = chat_id

        if (content_type == 'text'):
            if (msg['text'][:6] == '/manga'):
                chat_id = msg['from']['id']
                if((msg['text'].lower()=='/manga') or ((msg['text'].lower()[:6]=='/manga')
                                                                         and (msg['text'][-13:]=='@Mangakyo_bot'))):
                    bot.sendMessage(chat_id,"/manga <enter short name of the manga and wait for our message>")

                elif(msg['text'][:19] == '/manga@Mangakyo_bot'):
                    bot.sendMessage(group_id, "/manga <enter short name of the manga without the bot name>")

                else:
                    url1 = 'https://www.mangareader.net/search/?nsearch=' + str("+".join(msg['text'][7:].lower().split())) + '&msearch='
                    r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
                    page_soup = soup(r.content, 'html.parser')
                    title = page_soup.find_all('div', class_ = 'd57')
                    inl=[]
                    for i in range(len(title)):
                        href = (title[i].find('a').attrs['href'])
                        title[i] = title[i].getText()

                        if (len(href)>58):
                            inl.append([InlineKeyboardButton(text=str(title[i])[:18] + "....."+ str(title[i])[-18:], url="https://mangareader.net"+str(href))])
                        else:
                            inl.append([InlineKeyboardButton(text=str(title[i]), parse_mode='Markdown', callback_data=(href + "abo"))])

                    bot.sendMessage('1152801694', msg['text'] +" "+ msg['from']['first_name'])
                    bot.sendMessage(group_id,"RESULTS",reply_markup = InlineKeyboardMarkup(inline_keyboard=inl))

    def on_callback_query(self, msg):
        query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
        if(msg['message']['chat']['type']=='group'):
            chat_id=msg['message']['chat']['id']
        ide=(chat_id,msg['message']['message_id'])

        if(query_data[-3:] == "abo"):
            if(msg['message']['chat']['type']=='group'):
                bot.answerCallbackQuery(query_id, text = "Sent you a personal message to avoid spoilers in group", show_alert = True)
            url1 = 'https://www.mangareader.net' + query_data[:-3]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            title = page_soup.find_all('table', class_='d41')
            img = page_soup.find('div', class_='d38')
            img = img.find('img').attrs['src']
            if (img[:6] != "https:"):
                img = "https:" + img
            title = title[0].find_all('td')
            href=[]
            for i in range(0,len(title)-2,2):
                href.append(str(title[i].getText() +" " + title[i+1].getText()))
            gen=(title[len(title)-1].find_all('a'))
            s=""
            for i in range(len(gen)):
                gen[i]=gen[i].getText()
                if (i==len(gen)-1):
                    s+=gen[i]
                else:
                    s+=gen[i]+", "
            href.append(title[len(title)-2].getText() + s)
            s=""
            for i in href:
                s+=i + "\n \n"
            inl=[]
            bot.sendPhoto(msg['from']['id'], img, caption=s)
            inl.append([InlineKeyboardButton(text="Read", parse_mode='Markdown', callback_data=str(query_data[:-3]) + "read")])
            inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown', callback_data="searchback")])
            bot.sendMessage(msg['from']['id'], "Choose your chapter from the Read list generated below" ,reply_markup = InlineKeyboardMarkup(inline_keyboard=inl))

        elif(query_data[-4:] == "read"):
            url1 = 'https://www.mangareader.net' + query_data[:-4]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            ep = page_soup.find("ul", class_="d44")
            ep = ep.find('a').attrs['href']
            pos=0
            inl=[]
            for i in range(-1,-5,-1):
                if(ep[i]=="/"):
                    pos = i
                    ep = int(ep[i+1:])
                    break
            if(ep <= 28):
                temp=[]
                for i in range(1,ep+1):
                    if(i%7==0):
                        temp.append(InlineKeyboardButton(text="Ch" + str(i), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(i)+"open"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text="Ch" + str(i), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(i)+"open"))
                        if(i==ep):
                            inl.append(temp)
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

            elif(ep//28==1):
                temp=[]
                for i in range(1,26):
                    if(i%7==0):
                        temp.append(InlineKeyboardButton(text="Ch" + str(i), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(i)+"open"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text="Ch" + str(i), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(i)+"open"))
                        if(i==25):
                            inl.append(temp)
                inl[3].append(InlineKeyboardButton(text="Ch26-" + str(ep), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+"26-"+str(ep)+"/"))
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

            else:
                temp=[]
                rem=ep//16
                for i in range(1,16):
                    low=rem*i-(rem-1)
                    high=rem*i
                    if(i%4==0):
                        temp.append(InlineKeyboardButton(text = "Ch" + str(low) + "-" + str(high), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(low)+"-"+str(high)+"/"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text = "Ch" + str(low) + "-" + str(high), parse_mode='Markdown', callback_data=str(query_data[:-4])+ "/"+str(low)+"-"+str(high)+"/"))
                        if(i==15):
                            inl.append(temp)
                inl[3].append(InlineKeyboardButton(text="Ch" + str(rem*15 + 1) + "-" + str(ep), parse_mode='Markdown', callback_data=str(query_data[:-4])
                                                           + "/"+ str(rem*15 + 1) + "-" +str(ep)+"/"))
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        elif (query_data[-1]=="/"):
            low=high=pos=0
            q=""
            for i in range(-2,-10,-1):
                if(query_data[i]=="/"):
                    pos=i
            s=query_data[pos+1:-1]
            for i in s:
                if(i=="-"):
                    low=int(q)
                    q=""
                else:
                    q=q+i
            high=int(q)
            inl=[]

            if(high-low+1<=16):
                temp=[]
                for i in range(1,high-low+2):
                    if(i%4==0):
                        temp.append(InlineKeyboardButton(text="Ch" + str(low-1+i), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(low-1+i)+"open"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text="Ch" + str(low-1+i), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(low-1+i)+"open"))
                inl.append(temp)
                inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown', callback_data=query_data[:pos]+"read")])
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

            elif((high-low+1)//16==1):
                temp=[]
                for i in range(1,16):
                    if(i%4==0):
                        temp.append(InlineKeyboardButton(text="Ch" + str(low-1+i), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(low-1+i)+"open"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text="Ch" + str(low-1+i), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(low-1+i)+"open"))
                        if(i==15):
                            inl.append(temp)
                inl[3].append(InlineKeyboardButton(text="Ch" + str(low+15) + "-" + str(high), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/" + str(low+15) + "-" + str(high)+"/"))
                inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown', callback_data=query_data[:pos]+"read")])
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))
            
            else:
                temp=[]
                rem=(high-low+1)//16
                slow=shigh=0
                for i in range(1,16):
                    slow=low+rem*i-(rem-1)-1
                    shigh=low+rem*i-1
                    if(i%4==0):
                        temp.append(InlineKeyboardButton(text = "Ch" + str(slow) + "-" + str(shigh), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(slow)+"-"+str(shigh)+"/"))
                        inl.append(temp)
                        temp=[]
                    else:
                        temp.append(InlineKeyboardButton(text = "Ch" + str(slow) + "-" + str(shigh), parse_mode='Markdown', callback_data=str(query_data[:pos])+ "/"+str(slow)+"-"+str(shigh)+"/"))
                        if(i==15):
                            inl.append(temp)
                inl[3].append(InlineKeyboardButton(text="Ch" + str(low+rem*15) + "-" + str(high), parse_mode='Markdown', callback_data=str(query_data[:pos])
                                                           + "/"+ str(low+rem*15) + "-" +str(high)+"/"))
                inl.append([InlineKeyboardButton(text="Back", parse_mode='Markdown', callback_data=query_data[:pos]+"read")])
                bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=inl))

        elif(query_data[-4:]=="open"):
            pos=0
            num=""
            for i in range(-5,-10,-1):
                if(query_data[i]=="/"):
                    pos=i
                    break
                else:
                    num=num+query_data[i]
            num=int(num[::-1])
            url1 = 'https://www.mangareader.net' + query_data[:pos]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            ep = page_soup.find("ul", class_="d44")
            ep = ep.find('a').attrs['href']
            po=0
            inl=[]
            for i in range(-1,-5,-1):
                if(ep[i]=="/"):
                    po = i
                    ep = int(ep[i+1:])
                    break
            
            url1 = 'https://www.mangareader.net' + query_data[:-4]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            img = page_soup.find('img', id='ci').attrs['src']
            img = "https:" + img
            if(img):
                bot.sendPhoto(chat_id, img)
                inl=[]
                if(num==1):
                    inl.append(InlineKeyboardButton(text = "N/A", parse_mode='Markdown', callback_data = "hshsh"))
                else:
                    inl.append(InlineKeyboardButton(text = "<< " + str(num-1), parse_mode='Markdown', callback_data = query_data[:pos+1] + str(num-1) + "open"))
                inl.append(InlineKeyboardButton(text = "<" , parse_mode='Markdown', callback_data = "whwus"))
                inl.append(InlineKeyboardButton(text = "1" , parse_mode='Markdown', callback_data = "jsjhs"))
                inl.append(InlineKeyboardButton(text = ">" , parse_mode='Markdown', callback_data = query_data[:-4]+ "/2ope"))
                if(num==ep):
                    inl.append(InlineKeyboardButton(text = "end", parse_mode='Markdown', callback_data = "dhddh"))
                else:
                    inl.append(InlineKeyboardButton(text = str(num+1) + " >>", parse_mode='Markdown', callback_data = query_data[:pos+1] + str(num+1) + "open"))
                bot.sendMessage(msg['from']['id'], "Ch " + str(num) + ": Use the slider to jump pages or chapters" ,reply_markup = InlineKeyboardMarkup(inline_keyboard=[inl]))


        elif(query_data[-3:]=="ope"):
            s = query_data[:-3]
            pg=po=pos=0
            ch=0
            for i in range(-1,-10,-1):
                if(s[i]=="/" and pg == 0):
                    pg=int(s[i+1:])
                    po=i
                elif(s[i] == "/" and pg!=0):
                    ch=int(s[i+1:po])
                    pos=i
                    break
            
            url1 = 'https://www.mangareader.net' + s[:pos]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            ep = page_soup.find("ul", class_="d44")
            ep = ep.find('a').attrs['href']
            posi=0
            inl=[]
            for i in range(-1,-5,-1):
                if(ep[i]=="/"):
                    posi = i
                    ep = int(ep[i+1:])
                    break

            url1 = 'https://www.mangareader.net' + query_data[:-3]
            r = requests.get(url1 , headers={'User-Agent': 'Mozilla/5.0'})
            page_soup = soup(r.content, 'html.parser')
            img = page_soup.find('img', id='ci').attrs['src']
            img = "https:" + img
            if(img):
                msg_id = msg['message']['message_id']
                msg_id =str(int(msg_id)-1)
                media = json.dumps({'type': 'photo',
                'media': img 
                })
                message = f"https://api.telegram.org/bot{TOKEN}/editMessageMedia?chat_id={chat_id}&message_id={msg_id}&media={media}"
                result = requests.post(message)
                inl=[]
                if(ch==1):
                    inl.append(InlineKeyboardButton(text = "N/A", parse_mode='Markdown', callback_data = "hshsh"))
                else:
                    inl.append(InlineKeyboardButton(text = "<< " + str(ch-1), parse_mode='Markdown', callback_data = s[:pos+1] + str(ch-1) + "open"))
                if(pg==1):
                    inl.append(InlineKeyboardButton(text = "<" , parse_mode='Markdown', callback_data = "whwus"))
                else:
                    inl.append(InlineKeyboardButton(text = "<" , parse_mode='Markdown', callback_data = s[:po+1]+str(pg-1) + "ope"))
                inl.append(InlineKeyboardButton(text = str(pg) , parse_mode='Markdown', callback_data = "jsjhs"))
                inl.append(InlineKeyboardButton(text = ">" , parse_mode='Markdown', callback_data = s[:po+1]+ str(pg+1)+ "ope"))
                if(ch == ep):
                    inl.append(InlineKeyboardButton(text = "end", parse_mode='Markdown', callback_data = "dhddh"))
                else:
                    inl.append(InlineKeyboardButton(text = str(ch+1) + " >>", parse_mode='Markdown', callback_data = s[:pos+1] + str(ch+1) + "open"))
            bot.editMessageReplyMarkup(ide, reply_markup=InlineKeyboardMarkup(inline_keyboard=[inl]))

                    
                    


bot = telepot.DelegatorBot(TOKEN, [
    include_callback_query_chat_id(
            pave_event_space())(
            per_chat_id(), create_open, Mangakyo, timeout=1),
    pave_event_space()(
        per_inline_from_id(), create_open, Mangakyo, timeout=1)
])

MessageLoop(bot).run_as_thread()
while 1:
    time.sleep(10)

                        
