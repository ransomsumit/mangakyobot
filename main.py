import os
import re
import time
import json
import math
import telebot
import requests
import random
import pyshorteners
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
from io import BytesIO
from bs4 import BeautifulSoup as soup
from random import randint
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from telebot.types import InputMediaPhoto
from threading import Thread
from telebot import types


chilp_it = pyshorteners.Shortener()
token = os.environ.get("bot_api")
# token = "1324074534:AAH2WfmQT0M-Iv_H46iO0fz6qVStuvqeLY4"
bot = telebot.TeleBot(token)
holy = "https://w27.holymanga.net/"

def extract_text(text):
    if text.find('@') != -1:
        if(text.find("@mangak") != -1):
            text = re.sub("@mangakyo_bot","",text)
            return text.strip()
        else:
            return None
    return text.strip()


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "Howdy, " + message.from_user.first_name + ". Welcome to @Mangakyo_Bot. There is only one command '/manga'. \n\nEx. /manga one piece")


@bot.message_handler(commands=['manga'])
def manga_search(message):
    query_raw = re.sub("/manga","",message.text.lower())
    query_raw = extract_text(query_raw)
    if(query_raw == ""):
        bot.send_message(message.chat.id, "<  /manga Your Query  >")
    elif(query_raw == None):
        pass
    else:
        query = re.sub(" ", "+", query_raw.strip())
        req = requests.get(holy + "?s=" + str(query), headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
        sou = soup(req.content, "html.parser").find("div", class_ = "comics-grid").find_all("h3", class_ = "name")
        if(sou == []):
            bot.reply_to(message, "Nothing Found!! Make sure to type the name correct or in different keyword. Ask admins if persistent @Ransom_s")
        else:
            lis ={}
            markup = InlineKeyboardMarkup()
            for i in range(len(sou)):
                text = sou[i].find("a").getText()
                if len(text)>40:
                    text = text[:20] + "...." + text[-20:]
                url_full = sou[i].find("a").attrs["href"]
                url = re.sub(holy,'', url_full)
                if len(url)>40:
                    url = chilp_it.chilpit.short(url_full) +  "%ab#" + str(message.json['from']['id'])
                else:
                    url = url + "@ab#" + str(message.json['from']['id'])
                markup.add(InlineKeyboardButton(text, callback_data = url))
            bot.send_message(message.chat.id, "Results: " + query_raw, reply_markup=markup)


@bot.message_handler(commands=['read'])
def manga_reader(message):
    msgin = message.json['chat']['type']
    chat_id = message.json['chat']['id']
    msg_id = int(message.json['message_id'])
    url = re.sub("/read ", "", message.text)
    if (msgin == "group" or msgin == "supergroup"):
        bot.reply_to(message, "Sorry, manga reading is not allowed in groups 😭")
        return
    else:
        bot.delete_message(chat_id,msg_id)
        req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
        sou = soup(req.content, "html.parser").find("a", class_ = "bg-tt").getText()
        markup = InlineKeyboardMarkup()
        url_quotes = requests.utils.quote(url)
        markup.add(InlineKeyboardButton("Read Here", url = "https://animebot-play.herokuapp.com/mng/" + url_quotes))
        bot.send_message(chat_id, sou, parse_mode = "HTML", reply_markup=markup)


def manga_total_chap(url):
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser").find("div", class_ = "bg-white well")
    about = sou.find("div", class_ = "new-chap").getText().strip()
    num = int(re.findall(r'\d+', about)[0])
    return num


def manga_about(urlMain,typ,chat_id,msgin,clicker,message_id):
    bot.delete_message(chat_id,message_id)
    if typ == '@':
        url = holy + urlMain
    elif typ == '%':
        url = chilp_it.chilpit.expand(urlMain)
        urlMain = re.sub(holy,"",url)
        urlMain = re.sub("/","", urlMain)
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser").find("div", class_ = "bg-white well")
    img = sou.find("div", class_="thumb text-center").find("img").attrs['src']
    info = sou.find("div", class_ = "info")
    about = "<b>" + info.find("h1", class_="name bigger").getText() + "</b>\n"
    about += "<b>Rating: </b>" + info.find("div", class_ = "counter").getText() + "\n\n"
    about += "<b>" + info.find("div", class_ = "author").getText().strip().replace("\n","") + "</b>\n\n"
    about += "<b>" + info.find("div", class_ = "genre").getText().strip().replace("\n","") + "</b>\n\n"
    about += "<b>" + info.find("div", class_ = "new-chap").getText().strip() + "</b>\n"
    total_chap = manga_total_chap(url)
    about = about + "<pre>Approx " + str(math.ceil(total_chap/50)) + " pages of 50 results made</pre>\n\n"
    try:
        about += "<code>" + sou.find("div", class_ = "comic-description").find("p").getText() + "</code>"
    except Exception as e:
        about += "<code>" + sou.find("div", class_ = "comic-description").getText() + "</code>"

    try:
        url_white = "https://i.imgur.com/R1yA2Ik.jpeg"
        response = requests.get(url_white)
        background = Image.open(BytesIO(response.content))
        response = requests.get(img)
        poster = Image.open(BytesIO(response.content))
        back_width, back_height = background.size
        poster_width, poster_height = poster.size
        poster_resize_height_percent = back_height / poster_height
        resize_width = int((poster_width * poster_resize_height_percent) // 1)
        poster = poster.resize((resize_width, back_height))
        background.paste(poster)
        text = "MANGABOT"
        req = requests.get("https://drive.google.com/u/0/uc?id=1WPnro8tmf_bCmpSabblIYfauV8JZlnPq&export=download")
        with open('dacassa.ttf', 'wb') as f:
            f.write(req.content)
        font = ImageFont.truetype(r'dacassa.ttf', 35)
        draw = ImageDraw.Draw(background)
        rgb = (randint(0, 255), randint(0, 255), randint(0, 255))
        draw.text((resize_width + (back_width - resize_width) // 3.5, int(back_width * 0.30)), text, rgb, font = font, align="center")
        output = BytesIO()
        background.save(output, format="JPEG")
        output.seek(0)
    except Exception:
        pass
    markup = InlineKeyboardMarkup()
    if msgin == "group" or msgin == "supergroup":
        markup.add(InlineKeyboardButton("Start the Bot", url = "https://t.me/mangakyo_bot"))
        markup.add(InlineKeyboardButton("Select MangaBot after clicking this", switch_inline_query = urlMain))
    else:
        markup.add(InlineKeyboardButton("Read", switch_inline_query_current_chat = urlMain))

    try:
        bot.send_photo(chat_id, ('temp.jpg',output), caption = about, parse_mode = "HTML", reply_markup=markup)
    except Exception as e:
        bot.send_message(chat_id, about, parse_mode = "HTML", reply_markup=markup)
        print("Oops!", e.__class__, "occurred.")

def inline_extract(text):
    lis = text.split()
    if(len(lis) == 1):
        return lis[0],1
    return lis[0],lis[1]

def foo(url, lis, i):
    u = url + "/page-" + str(i) + "/"
    req = requests.get(u, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser").find_all("h2", class_ = "chap")
    temp = {}
    for j in sou:
        temp[j.find("a").getText()]= j.find("a").attrs['href']
    lis[i] =  temp

def count_chapters(url):
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    try:
        num = soup(req.content, "html.parser").find("div", class_ = "pagination").find_all("a", class_ = "next page-numbers")[1].attrs['href']
        num = int(num[num.find('page-')+5:])
    except Exception as e:
        num = 1
    threads = [None] * num
    lis = {}
    for i in range(1,num+1):
        threads[i-1] = Thread(target=foo, args=(url, lis, i))
        threads[i-1].start()
    for i in range(len(threads)):
        threads[i].join()
    temp = {}
    for i in range(1,len(lis)+1):
        temp = {**temp, **lis[i]}
    return temp

def manga_chap(in_id,name,page):
    url = holy + name
    lis = count_chapters(url)
    chapters_name = list(lis.keys())
    total = len(chapters_name)
    r = []
    if total>50*page:
        for i in range(50*(page-1),50*page):
            r.append(types.InlineQueryResultArticle(i+1, chapters_name[i][:20] + "..." + chapters_name[i][-20:], types.InputTextMessageContent('/read ' + lis[chapters_name[i]])))
    elif (total>50*(page-1) and 50*page>total):
        for i in range(50*(page-1),total):
            r.append(types.InlineQueryResultArticle(i+1, chapters_name[i][:20] + "..." + chapters_name[i][-20:], types.InputTextMessageContent('/read ' + lis[chapters_name[i]])))
    elif total<50*(page-1):
        r.append(types.InlineQueryResultArticle(1, "Page out of range", types.InputTextMessageContent("oops!! Wrong page")))
    bot.answer_inline_query(in_id, r)


def query_extract(text):
    text = text[:text.find("#")]
    command = text[-2:]
    typ = text[-3]
    url = text[:-3]
    return url,typ,command


@bot.callback_query_handler(func=lambda call: True)
def query_handler(query):
    query_text = query.data
    message_id = query.message.message_id
    msgin = query.message.json['chat']['type']
    group_id = query.message.json['chat']['id']
    owner = query_text[query_text.find("#")+1:]
    clicker = str(query.from_user.id)
    if(clicker != owner):
        bot.answer_callback_query(query.id, "Not Your Query!!", show_alert = True)
    else:
        url,typ,cmd = query_extract(query_text)
        if cmd == "ab":
            try:
                manga_about(url,typ,group_id,msgin,clicker,message_id)
            except Exception as e:
                bot.answer_callback_query(query.id, "Error Occured", show_alert = True)

@bot.inline_handler(lambda query: query.query)
def query_text(inline_query):
    in_query, page = inline_extract(inline_query.query)
    try:
        manga_chap(inline_query.id, in_query.lower(), int(page))
    except Exception as e:
        r = types.InlineQueryResultArticle('1', "Make Sure to follow correct syntax, name + pageNo. with a space", types.InputTextMessageContent('Make Sure to follow correct syntax, name + pageNo. with a space \nError: ' + str(e)))
        r2 = types.InlineQueryResultArticle('2', 'Example : one-piece 11', types.InputTextMessageContent('Something went wrong ' + str(e)))
        bot.answer_inline_query(inline_query.id, [r,r2])

bot.polling(none_stop = True)
