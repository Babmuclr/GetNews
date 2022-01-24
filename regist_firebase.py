import hashlib

def regist_firebase(db, articles, database):
    for article in articles:
        title = article["guid"]
        hash_val = hashlib.sha224(title.encode()).hexdigest()
        with open("/Users/takumiinui/Desktop/get_news/articles/" + database + ".txt", "r") as f:
            x = f.read()
        hash_li = list(x.split("\n"))[:-1]
        # if True:
        if hash_val not in hash_li:
            with open("/Users/takumiinui/Desktop/get_news/articles/" + database + ".txt", "a", newline="") as f:
                f.write(hash_val+"\n")
            doc_ref = db.collection(database).document()
            doc_ref.set({
                u"title": article["title"],
                u"pubDate": article["pubDate"],
                u"link": article["link"],
                u"source": article["source"],
                u"title_ja": article["japanese_title"], 
                u"top_image": article["top_image"], 
            })