from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import lxml # xmlを扱うためのlxmlをインポート
import datetime as dt
import hashlib

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import os

STOCKS_FILE_PATH = "/Users/takumiinui/Desktop/get_news/stocks.txt"
NEWS_SITE_FILE_PATH = "/Users/takumiinui/Desktop/get_news/news_site.txt"

with open(STOCKS_FILE_PATH) as f:
    STOCKS = f.readlines()
STOCKS = list(map(lambda x: x[:-1],STOCKS))
        
with open(NEWS_SITE_FILE_PATH) as f:
    NEWS_SITE = f.readlines()
NEWS_SITE = list(map(lambda x: x[:-1],NEWS_SITE))

WEBSITE = [" - Reuters", " - Bloomberg", " - CNBC", " - TheStreet", " - Fox Business"," - The Wall Street Journal"," - Forbes"," - Business Insider", " - Motley Fool"]
WEBSITE_SOURCE = ["Reuters", "Bloomberg", "CNBC", "TheStreet", "FoxBusiness","TheWallStreetJournal","Forbes","BusinessInsider", "MotleyFool"]

# 時間関係の設定
NOW = dt.datetime.utcnow() - dt.timedelta(days=1)
FREE_DAY = dt.datetime.utcnow() - dt.timedelta(weeks=2)
YEAR, MONTH, DAY = NOW.year, NOW.month, NOW.day
LIMIT_DATE = str(YEAR) + "-" + str(MONTH) + "-" + str(DAY)
FREE_YEAR, FREE_MONTH, FREE_DAY = FREE_DAY.year, FREE_DAY.month, FREE_DAY.day
FREE_DATE = str(FREE_YEAR) + "-" + str(FREE_MONTH) + "-" + str(FREE_DAY)

# deeplを使うときの設定
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.105 Safari/537.36'
}
sleep_time = 10
try_max_count = 30
from_lang = 'en'
to_lang = 'ja'

# ファイアベースに登録するためのやつ
cred = credentials.Certificate("/Users/takumiinui/Desktop/get_news/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def main():
    important_articles = get_google_news_xml(query="", date=LIMIT_DATE, limit=3)
    print("latest sucessed")
    time.sleep(10)
    
    website_articles = []
    for i,j,k in zip(NEWS_SITE,WEBSITE,WEBSITE_SOURCE):
        website_articles.append(get_google_news_xml_from_one_website(query=i, date=FREE_DATE, newssite=i,website=j,website2=k,limit=5))
        time.sleep(10)
    print("website sucessed")
    
    stocks_articles = []
    for i in STOCKS:
        stocks_articles += get_google_news_xml(query=i, date=FREE_DATE, limit=1)
        time.sleep(10)
    print("earings sucessed")
    
    regist_firebase(articles=important_articles, database="importants")
    print("latest sucessed")
    
    for i, j in zip(website_articles, WEBSITE_SOURCE):
        regist_firebase(articles=i, database=j)
    print("earnings sucessed")
    
    regist_firebase(articles=stocks_articles, database="earnings")
    
    print("earings sucessed")
    print("Completed")
    print(NOW)
    
def get_items(query="Apple", date="2021-1-1", homepage="reuters.com"):
    query = urllib.parse.quote(query)
    url = "https://news.google.com/rss/search?q=" + query +  "+after:" + date + "+inurl:" + homepage + "&hl=en-US&gl=US&ceid=US:en"
    try:
        response = request.urlopen(url)
        soup = BeautifulSoup(response,"xml")
        response.close()
        elems = soup.find_all("item")
    except Exception as e:
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
            f.write("url:  ", url)
            f.write ('=== エラー内容 ===')
            f.write ('type:' + str(type(e)))
            f.write ('args:' + str(e.args))
            f.write ('message:' + e.message)
            f.write ('e自身:' + str(e))
    return elems

# https://news.google.com/rssに出力される記事の一覧を手に入れる
def get_google_news_xml(query, date, limit):
    articles = []
    for news_site, website_name, website_name_2 in zip(NEWS_SITE, WEBSITE, WEBSITE_SOURCE):
        items = get_items(query=query, date=date, homepage=news_site)
        for item in items[:limit]:
            title = item.find("title").getText()
            title = str(title.replace(website_name,""))
            link = item.find("link").getText()
            pubdate = dt.datetime.strptime(item.find("pubDate").getText(), '%a, %d %b %Y %H:%M:%S %Z')
            articles.append(
                {
                    "title": title,
                    "pubDate": pubdate,
                    "source": website_name_2,
                    "link": link,
                }
            )
    titles = ""
    for article in articles:
        article = article["title"].replace("/","")
        article = article.replace("|","")
        titles += (article+"\n")
    japanese_title = list(get_translated_text(from_lang, to_lang, titles).split("\n"))
    try:
        for i in range(len(articles)):
            articles[i]["japanese_title"] = japanese_title[i]
    except Exception as e:
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
            f.write("titles:  ", titles)
            f.write("articles:  ", articles)
            f.write ('=== エラー内容 ===')
            f.write ('type:' + str(type(e)))
            f.write ('args:' + str(e.args))
            f.write ('message:' + e.message)
            f.write ('e自身:' + str(e))
    return articles

def get_google_news_xml_from_one_website(query, date, newssite, website, website2, limit):
    articles = []
    items = get_items(query=query, date=date, homepage=newssite)
    for item in items[:limit]:
        title = item.find("title").getText()
        title = str(title.replace(website,""))
        link = item.find("link").getText()
        pubdate = dt.datetime.strptime(item.find("pubDate").getText(), '%a, %d %b %Y %H:%M:%S %Z')
        articles.append(
            {
                "title": title,
                "pubDate": pubdate,
                "source": website2,
                "link": link,
            }
        )
    titles = ""
    for article in articles:
        article = article["title"].replace("/","")
        article = article.replace("|","")
        titles += (article+"\n")
    japanese_title = list(get_translated_text(from_lang, to_lang, titles).split("\n"))
    try:
        for i in range(len(articles)):
            articles[i]["japanese_title"] = japanese_title[i]
    except Exception as e:
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
            f.write("titles:  ", titles)
            f.write("articles:  ", articles)
            f.write ('=== エラー内容 ===')
            f.write ('type:' + str(type(e)))
            f.write ('args:' + str(e.args))
            f.write ('message:' + e.message)
            f.write ('e自身:' + str(e))
    return articles

def regist_firebase(articles, database):
    for article in articles:
        title = article["title"]
        hash_val = hashlib.sha224(title.encode()).hexdigest()
        with open("/Users/takumiinui/Desktop/get_news/articles/" + database + "/articles.txt", "r") as f:
            x = f.read()
        hash_li = list(x.split("\n"))[:-1]
        if hash_val not in hash_li:
            with open("/Users/takumiinui/Desktop/get_news/articles/" + database + "/articles.txt", "a", newline="") as f:
                f.write(hash_val+"\n")
            doc_ref = db.collection(database).document()
            doc_ref.set({
                u"title": article["title"],
                u"pubDate": article["pubDate"],
                u"link": article["link"],
                u"source": article["source"],
                u"title_ja": article["japanese_title"], 
            })
    
def get_translated_text(from_lang, to_lang, from_text):
     
    # urlencode
    from_text = urllib.parse.quote(from_text)
     
    #　url作成
    url = 'https://www.deepl.com/translator#' + from_lang +'/' + to_lang + '/' + from_text
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
     
    # ブラウザーを起動
    driver = webdriver.Chrome('/Users/takumiinui/Desktop/get_news/chromedriver', options=options)
    driver.get(url)
    driver.implicitly_wait(30)  # 見つからないときは、30秒まで待つ
 
    for i in range(try_max_count):
         
        # 指定時間待つ
        time.sleep(sleep_time)  
        html = driver.page_source
        to_text = get_text_from_page_source(html)
         
        try_count = i + 1
     
        if to_text:
            wait_time =  sleep_time * try_count
            # print(str(wait_time) + "秒")
             
            # アクセス修了
            break
             
    # ブラウザ停止
    driver.quit()
     
    return to_text

def get_text_from_page_source(html):
    soup = BeautifulSoup(html, features='lxml')
    target_elem = soup.find(class_="lmt__translations_as_text__text_btn")
    text = target_elem.text
     
    return text
    

main()