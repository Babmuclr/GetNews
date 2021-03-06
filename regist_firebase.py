import hashlib

def regist_firebase(db, articles, database):
    for article in articles:
        hash_val1 = hashlib.sha224(article["guid"].encode()).hexdigest()
        hash_val2 = hashlib.sha224(article["title"].encode()).hexdigest()
        hash_val3 = hashlib.sha224(article["link"].encode()).hexdigest()
        
        with open("/Users/takumiinui/Desktop/get_news/articles/" + database + ".txt", "r") as f:
            x = f.read()
        hash_li = list(x.split("\n"))[:-1]
        # if True:
        if (hash_val1 not in hash_li) and (hash_val2 not in hash_li) and (hash_val3 not in hash_li):
            with open("/Users/takumiinui/Desktop/get_news/articles/" + database + ".txt", "a", newline="") as f:
                f.write(hash_val1+"\n")
                f.write(hash_val2+"\n")
                f.write(hash_val3+"\n")
            doc_ref = db.collection(database).document()
            doc_ref.set({
                u"title": article["title"],
                u"pubDate": article["pubDate"],
                u"link": article["link"],
                u"source": article["source"],
                u"title_ja": article["japanese_title"], 
                u"top_image": article["top_image"], 
            })