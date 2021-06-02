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
from telebot import types
from selenium import webdriver


chilp_it = pyshorteners.Shortener()
#token = os.environ.get("bot_api")
token = "1867991747:AAHphYJWpTkxeUaV0D9RhtBveTeMIY_N3dg"
bot = telebot.TeleBot(token)
chrome_options = webdriver.ChromeOptions()
chrome_options.binary_location = os.environ.get("CHROME_BIN")
chrome_options.add_argument("--headless")
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--no-sandbox')
browser = webdriver.Chrome(executable_path=os.environ.get("CHROME_PATH"), chrome_options = chrome_options)

def extract_text(text):
    if text.find('@') != -1:
        if(text.find("@manga") != -1):
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
        req = requests.get("http://fanfox.net/search?title=&genres=&nogenres=&sort=&stype=1&name=" + str(query)
                           + "&type=0&author_method=cw&author=&artist_method=cw&artist=&rating_method=eq&rating=&released_method=eq&released=&st=0",
                           headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
        sou = soup(req.content, "html.parser").find("ul", class_="manga-list-4-list line")
        if(sou == None):
            bot.reply_to(message, "Nothing Found!! Make sure to type the name correct. Ask admins if persistent @Ransom_s")
        else:
            sou = sou.find_all("li")
            lis ={}
            markup = InlineKeyboardMarkup()
            for i in range(len(sou)):
                text = sou[i].find("p").getText()
                url_full = "http://fanfox.net" + sou[i].find("a").attrs["href"]
                url = re.sub('/manga/',"", sou[i].find("a").attrs["href"][:-1])
                if len(url)>40:
                    url = chilp_it.chilpit.short(url_full) +  "%ab#" + str(message.json['from']['id'])
                else:
                    url = url + "@ab#" + str(message.json['from']['id'])
                markup.add(InlineKeyboardButton(text, callback_data = url))
            bot.send_message(message.chat.id, "Results: " + query_raw, reply_markup=markup)

def loading(text,chat_id,msg_id):
    bot.edit_message_text(text,str(chat_id), msg_id) 

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
        msg_id = bot.send_message(chat_id, "Parsing Pages ⌛")
        msg_id = int(msg_id.message_id)
        req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
        sou = soup(req.content, "html.parser")
        sou = sou.find("div", class_ = "pager-list cp-pager-list").find("span").find_all("a")
        max_page = int(sou[len(sou)-2].getText())
        loading("Total pages found: " + str(max_page) + "\nImage Scraping Started....", chat_id, msg_id)
        images ={}
        for i in range(1,max_page+1):
            url1 = url[:-6] + str(i) + ".html"
            ch = random.choice(["Amaterasu","Kagutsuchi","Tsukuyomi","Izanagi","Izanami","Kotoamatsukami","Susanoo","Indra's Yajirushi","Chidori",
                                "Rasengan","Flying Raijin","REAPER DEATH SEAL","SHINRA TENSEI","KAMUI","TENGAI SHINSEI","AMENOMINAKA"])
            loading("Image Loading Jutsu......\n\nLoading " + ch + " ......" + str(i) + " out of " + str(max_page), chat_id, msg_id)
            browser.get(url1)
            time.sleep(2)
            req = browser.page_source
            sou = soup(req, "html.parser")
            sou = "http:" + sou.find("img", class_ = "reader-main-img").attrs['src']
            images[i] = sou
        temp = []
        ind = []
        image_list = list(images.keys())
        for i in range(len(image_list)):
            if(i%10 == 0 and i!=0):
                ind.append(temp)
                temp=[]
            temp.append(InputMediaPhoto(media = images[image_list[i]], caption = image_list[i]))
        if(len(temp) !=0):
            ind.append(temp)
            temp=[]
        bot.delete_message(chat_id,msg_id)
        for i in ind:
            bot.send_media_group(chat_id, i)
            
            
        
def manga_total_chap(url):
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser")
    if(sou.find("a", {"id":"checkAdult"}) != None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.binary_location = os.environ.get("CHROME_BIN")
        chrome_options.add_argument("--headless")
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--no-sandbox')
        browser = webdriver.Chrome(executable_path=os.environ.get("CHROME_PATH"), chrome_options = chrome_options)
        browser.get(url)
        browser.find_element_by_link_text("Please click here to continue reading.").click()
        req = browser.page_source
        sou = soup(req, "html.parser")
        browser.quit()

    sou = sou.find("ul", class_ = "detail-main-list").find_all("li")
    return len(sou)


def manga_about(urlMain,typ,chat_id,msgin,clicker,message_id):
    bot.delete_message(chat_id,message_id)
    if typ == '@':
        url = "http://fanfox.net/manga/" + urlMain
    elif typ == '%':
        url = chilp_it.chilpit.expand(urlMain)
        urlMain = re.sub("http://fanfox.net/manga/","",url[:-1])
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser")
    img = sou.find("div", class_ = "detail-info-cover").find("img").attrs['src']
    abo = sou.find("div", class_ = "detail-info-right").find_all("p")
    about = "<b>" + abo[0].getText().strip() + "</b>\n\n"
    about = about + "<b>" + abo[1].getText().strip() + "</b>\n\n"
    about = about + "<b>Genre:<i> " + abo[2].getText().strip() + "</i></b>\n\n"
    total_chap = manga_total_chap(url)
    about = about + "<b>Total Chapters Found: </b>" + "<i>" + str(total_chap) + "</i>\n"
    about = about + "<pre>Approx " + str(math.ceil(total_chap/50)) + " pages of 50 results made</pre>\n\n"
    about = about + '<code>' + abo[3].getText().strip()+ "</code>\n"

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

def manga_chap(in_id,name,page):
    url = "http://fanfox.net/manga/" + name
    req = requests.get(url, headers = {"User-Agent" : "Mozilla/5.0", 'x-requested-with': 'XMLHttpRequest'})
    sou = soup(req.content, "html.parser")
    if(sou.find("a", {"id":"checkAdult"}) != None):
        r = [types.InlineQueryResultArticle(1, "18+ Content, Click Here and Read on Website", types.InputTextMessageContent(url))]
        bot.answer_inline_query(in_id, r)
        return 0
    sou = sou.find("ul", class_ = "detail-main-list").find_all("li")
    lis={}
    for i in range(len(sou)):
        lis[sou[i].find("p").getText()] = "http://fanfox.net" + sou[i].find("a").attrs['href']
    chapters_name = list(lis.keys())
    total = len(chapters_name)
    r = []
    if total>50*page:
        for i in range(50*(page-1),50*page):
            r.append(types.InlineQueryResultArticle(i+1, chapters_name[i], types.InputTextMessageContent('/read ' + lis[chapters_name[i]])))
    elif (total>50*(page-1) and 50*page>total):
        for i in range(50*(page-1),total):
            r.append(types.InlineQueryResultArticle(i+1, chapters_name[i], types.InputTextMessageContent('/read ' + lis[chapters_name[i]])))
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
        r = types.InlineQueryResultArticle('1', "Make Sure to follow correct syntax, name + pageNo. with a space", types.InputTextMessageContent('Something went wrong ' + str(e)))
        r2 = types.InlineQueryResultArticle('2', 'Example : one_piece 11', types.InputTextMessageContent('Something went wrong ' + str(e)))
        bot.answer_inline_query(inline_query.id, [r,r2])

bot.polling(none_stop = True)
