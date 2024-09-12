from bs4 import BeautifulSoup
import requests
import discord
import random

class GetManhawa:

    def __init__(self):
        self.host = "https://manga168.net/manga/"
        self.number_picture = 2
    
    def changeTitleWeb(self, title: str):
        if " – " in title:
            title = title.split(" – ")
            title = " ".join(title)
        if "’" in title:
            title = title.split("’")
            title = "".join(title)
        if "'" in title:
            title = title.split("’")
            title = "".join(title)
        title_web = "-".join(title.lower().split(" "))
        return title_web
    
    def getInfoManhwa(self, title: str):
        title_web = self.changeTitleWeb(title)
        url = self.host + title_web
        res = requests.get(url)
        soup = BeautifulSoup(res.text, 'html.parser')
        datas = soup.find_all("img", {"class": "attachment- size- wp-post-image"})
        print(datas)
        link = str(datas[0]).split('src="')[1].split('"')[0]
        return url, link