# GetNews

ニュース記事を取得し、タイトルを翻訳する。10分毎にスクレイピングを行い、ニュースデータを取得する。取得後、タイトルの翻訳とニュース記事のTwitterへの投稿する。

取得には、[Google News API](https://news.google.com/rss/)を採用し、BeautifulSoupを用いて実行する。取得後の翻訳は、Seleniumを使って、DeepLの翻訳機能を活かした翻訳を行う。それぞれ、Qiitaに機能をまとめている。

- [ニュース記事をスクレイピング](https://qiita.com/inuit/items/64a8833bfe7a7e32f09e)
- [SeleniumでDeepL翻訳](https://qiita.com/inuit/items/41bed1261be4e1c73a06)

このデータをFirebaseに保存する。Firebaseには、[参考記事](https://qiita.com/inuit/items/9c3ea648192747dacdf4)で行う。また、Twitterへの投稿は、TwitterAPIを用いて行う。
