import requests
from bs4 import BeautifulSoup
from pymongo import MongoClient
from datetime import datetime

client = MongoClient(host="localhost", port=27017)
db = client.myweb
col = db.board


header = {"user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"}
for i in range(10):
    url = "https://www.google.com/search?q={}&start={}".format("파이썬", 10 * i)
    r = requests.get(url, headers=header)
    bs = BeautifulSoup(r.text, "lxml")
    lists = bs.select("div#search div.MjjYud")     
    # 제목을 바로 가져오는게 아니라 list를 가지고오고
    # 제목 크롤링
    # 내용 크롤링
    
    
    
    for l in lists:
        current_utc_time = round(datetime.utcnow().timestamp() * 1000)
        
        try:
            title = l.select_one("h3").text
            contents = l.select_one("div.VwiC3b").text
            col.insert_one({
                "name": 'test',
                "title": title,
                'contents': contents,
                'view': 0,
                "pubdate": current_utc_time
            })
            
        except:
            pass


