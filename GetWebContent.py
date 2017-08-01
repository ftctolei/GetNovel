#-*- coding: utf-8 -*-
import urllib2
from bs4 import BeautifulSoup
import demjson as json

url="http://bbs.tianya.cn/m/post-16-1667691-2.shtml"
#url="http://bbs.tianya.cn/m/post-16-1667691-1.shtml"
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

floorClassName = 'item item-ht item-lz'
floorContentDIVName = 'reply-div'

floorIDName = 'data-id'
floorUserName = 'data-user'

floorDIV = soup.find_all(name='div',attrs={"class":floorClassName})
#print floorDIV

for floor in floorDIV:
    dataID = floor.attrs[floorIDName]
    dataUser = floor.attrs[floorUserName]
    #print dataID
    #print dataUser

    floorContent = floor.find(name='div',attrs={"class":floorContentDIVName}).get_text()
    print floorContent

