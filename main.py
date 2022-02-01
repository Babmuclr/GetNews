from urllib import request  # urllib.requestモジュールをインポート
from bs4 import BeautifulSoup  # BeautifulSoupクラスをインポート
import lxml # xmlを扱うためのlxmlをインポート
import datetime as dt

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import urllib.parse
import os
from newspaper import Article
import argparse

import translate
import regist_firebase

parser = argparse.ArgumentParser(description='GET NEWS DATA AND RESIST THE NEWS')
parser.add_argument('-m', "--mode", type=str, default='MACOS',
                    help="select the envs" )
args = parser.parse_args()

if args.mode == "MACOS":
    DRIVER_PATH = '/Users/takumiinui/Desktop/get_news/chromedriver'
elif args.mode == "M1":
    DRIVER_PATH = '/Users/takumiinui/Desktop/get_news/chromedriver_m1'

NEWS_SITE_FILE_PATH = "/Users/takumiinui/Desktop/get_news/news_site.txt" 
        
with open(NEWS_SITE_FILE_PATH) as f:
    NEWS_SITE = f.readlines()

# ニュースサイトのリスト
NEWS_SITE = list(map(lambda x: x[:-1],NEWS_SITE))
WEBSITE = [" - Reuters", " - CNBC", " - TheStreet", " - Fox Business"," - CNN"," - HuffPost"," - Bloomberg",]
WEBSITE_SOURCE = ["Reuters", "CNBC", "TheStreet", "FoxBusiness","CNN","HuffPost","Bloomberg",]

# 時間関係の設定
NOW = dt.datetime.utcnow() - dt.timedelta(days=2)
FREE_DAY = dt.datetime.utcnow() - dt.timedelta(weeks=2)
YEAR, MONTH, DAY = NOW.year, NOW.month, NOW.day
LIMIT_DATE = str(YEAR) + "-" + str(MONTH) + "-" + str(DAY)
FREE_YEAR, FREE_MONTH, FREE_DAY = FREE_DAY.year, FREE_DAY.month, FREE_DAY.day
FREE_DATE = str(FREE_YEAR) + "-" + str(FREE_MONTH) + "-" + str(FREE_DAY)

# ファイアベースに登録するためのやつ
cred = credentials.Certificate("/Users/takumiinui/Desktop/get_news/serviceAccountKey.json")
firebase_admin.initialize_app(cred)
db = firestore.client()

def main():
    important_articles = get_google_news_xml(query="", date=LIMIT_DATE, limit=3)
    print("latest sucessed")
    time.sleep(5)
    
    website_articles = []
    for i,j,k in zip(NEWS_SITE,WEBSITE,WEBSITE_SOURCE):
        website_articles.append(get_google_news_xml_from_one_website(query="", date=FREE_DATE, newssite=i,website=j,website2=k,limit=15))
        time.sleep(5)
    print("website sucessed")
    
    regist_firebase.regist_firebase(db, articles=important_articles, database="importants")
    print("latest sucessed")
    
    for i, j in zip(website_articles, WEBSITE_SOURCE):
        regist_firebase.regist_firebase(db, articles=i, database=j)
    print("website sucessed")
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
        elems=[]
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
            f.write ('=== エラー内容 ==='+ "\n")
            f.write ('type:' + str(type(e)) + "\n")
            f.write ('args:' + str(e.args) + "\n")
            f.write ('e自身:' + str(e) + "\n")
            f.write ('url:' + str(url) + "\n")
    return elems

# https://news.google.com/rssに出力される記事の一覧を手に入れる
def get_google_news_xml(query, date, limit):
    articles = []
    for news_site, website_name, website_name_2 in zip(NEWS_SITE, WEBSITE, WEBSITE_SOURCE):
        items = get_items(query=query, date=date, homepage=news_site)
        if items == []:
            continue
        elif len(items) > limit:
            items = items[:limit]
            
        for item in items:
            title = item.find("title").getText()
            title = str(title.replace(website_name,""))
            link = item.find("link").getText()
            guid = item.find("guid").getText()
            pubdate = dt.datetime.strptime(item.find("pubDate").getText(), '%a, %d %b %Y %H:%M:%S %Z')
            try:
                article_data = Article(link)
                article_data.download()
                article_data.parse()
                top_image = article_data.top_image
            except Exception as e:
                top_image = ""
                with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
                    f.write ('=== エラー内容 ==='+ "\n")
                    f.write ('type:' + str(type(e)) + "\n")
                    f.write ('args:' + str(e.args) + "\n")
                    f.write ('e自身:' + str(e) + "\n")
            articles.append(
                {
                    "title": title,
                    "pubDate": pubdate,
                    "source": website_name_2,
                    "link": link,
                    "top_image": top_image,
                    "guid": guid,
                }
            )
                    
    titles = ""
    for article in articles:
        article = article["title"].replace("/","")
        article = article.replace("|","")
        titles += (article+"\n")
    japanese_titles = translate.get_translated_text( titles, DRIVER_PATH).split("\n")
    japanese_title = list(japanese_titles)
    try:
        for i in range(len(articles)):
            articles[i]["japanese_title"] = japanese_title[i]
    except Exception as e:
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f:
            f.write ('=== エラー内容 ==='+ "\n")
            f.write ('type:' + str(type(e)) + "\n")
            f.write ('args:' + str(e.args) + "\n")
            f.write ('e自身:' + str(e) + "\n")
            f.write ('タイトル:' + str(titles) + "\n")
            f.write ('日本語タイトル:' + str(japanese_titles) + "\n")
    return articles

# https://news.google.com/rssに出力される記事の一覧を手に入れる
def get_google_news_xml_from_one_website(query, date, newssite, website, website2, limit):
    articles = []
    
    items = get_items(query=query, date=date, homepage=newssite)
    if items == []:
        return []
    elif len(items) > limit:
        items = items[:limit]
        
    for item in items:
        title = item.find("title").getText()
        title = str(title.replace(website,""))
        link = item.find("link").getText()
        guid = item.find("guid").getText()
        pubdate = dt.datetime.strptime(item.find("pubDate").getText(), '%a, %d %b %Y %H:%M:%S %Z')
        try:
            article_data = Article(link)
            article_data.download()
            article_data.parse()
            top_image = article_data.top_image
        except Exception as e:
            top_image = ""
            with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
                f.write ('=== エラー内容 ==='+ "\n")
                f.write ('type:' + str(type(e)) + "\n")
                f.write ('args:' + str(e.args) + "\n")
                f.write ('e自身:' + str(e) + "\n")
        articles.append(
            {
                "title": title,
                "pubDate": pubdate,
                "source": website2,
                "link": link,
                "top_image": top_image,
                "guid": guid,
            }
        )
    titles = ""
    for article in articles:
        article = article["title"].replace("/","")
        article = article.replace("|","")
        titles += (article+"\n")
    japanese_titles = translate.get_translated_text( titles, DRIVER_PATH).split("\n")
    japanese_title = list(japanese_titles)
    try:
        for i in range(len(articles)):
            articles[i]["japanese_title"] = japanese_title[i]
    except Exception as e:
        with open("/Users/takumiinui/Desktop/get_news/errors.txt", "a") as f: 
            f.write ('=== エラー内容 ==='+ "\n")
            f.write ('type:' + str(type(e)) + "\n")
            f.write ('args:' + str(e.args) + "\n")
            f.write ('e自身:' + str(e) + "\n")
            f.write ('タイトル:' + str(titles) + "\n")
            f.write ('日本語タイトル:' + str(japanese_titles) + "\n")
    return articles

main()