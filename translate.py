import time
import urllib.parse

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from bs4 import BeautifulSoup

# deeplを使うときの設定
sleep_time = 5
try_max_count = 10
from_lang = 'en'
to_lang = 'ja'

def get_translated_text(from_text, DRIVER_PATH):
    # urlencode
    from_text = urllib.parse.quote(from_text)
    url = 'https://www.deepl.com/translator#' + from_lang +'/' + to_lang + '/' + from_text
     
    #　ヘッドレスモードでブラウザを起動
    options = Options()
    options.add_argument('--headless')
    
    # ブラウザーを起動
    driver = webdriver.Chrome(DRIVER_PATH, options=options)
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

def check(x):
    print(x)