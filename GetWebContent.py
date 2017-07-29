#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import demjson as json

url="http://bbs.tianya.cn/m/post-16-1667691-212.shtml"
htmlContent=urllib2.urlopen(url)
soup = BeautifulSoup(htmlContent,"lxml")
bbsGlobalDict = soup.script.contents[0].string.replace('var bbsGlobal = ','').replace(';','')
user_dict = json.decode(bbsGlobalDict)

totalPage = user_dict['totalPage']
authorName = user_dict['authorName']
title = user_dict['title']
subType = user_dict['subType']

print totalPage
#print authorName
#print title
#print subType
#print soup

contentDIV = soup.find_all(name='div',attrs={"class":"reply-div"})

for div in contentDIV:
    print div.p