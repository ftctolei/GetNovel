#-*- coding: utf-8 -*-
import logging
import sys
import urllib2

import demjson as json
from bs4 import BeautifulSoup

log_file = "./logs/GetNovel.log"
#TODO 判断日志文件是否存在

log_level = logging.DEBUG
logger = logging.getLogger("loggingmodule.NomalLogger")
handler = logging.FileHandler(log_file)
formatter = logging.Formatter("[%(levelname)s][%(funcName)s][%(asctime)s]%(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(log_level)


def getBsSoup(url):
    try:
        htmlContent = urllib2.urlopen(url)
    except urllib2.HTTPError, e:
        logger.error('get url content failed : ' + str(e.code))
        sys.exit()
    except urllib2.URLError, e:
        logger.error('get url content failed : ' + str(e.reason))
        sys.exit()
    soup = BeautifulSoup(htmlContent, "lxml")
    return soup

#匹配天涯移动版 莲蓬鬼话 板块 帖子<<没有名字的人 >>
#传入每页地址，返回回复是楼主的楼层内容
def getTiantaPageContent(bsSoup ):
    floorClassName = 'item item-ht item-lz'
    floorContentDIVName = 'reply-div'
    floorIDName = 'data-id'
    floorUserName = 'data-user'

    floorDIV = bsSoup.find_all(name='div', attrs={"class": floorClassName})
    resultContent = ''
    dataID = ''
    for floor in floorDIV:
        #dataUser = floor.attrs[floorUserName]
        dataID = floor.attrs[floorIDName]
        floorContent = floor.find(name='div', attrs={"class": floorContentDIVName}).get_text()
        resultContent = resultContent + floorContent

    floorContentmap ={'floorID':dataID,'pageContent':resultContent}
    return floorContentmap

floorContentmap = {}
def getPageTotal(bsSoup):
    bbsGlobalDict = bsSoup.script.contents[0].string.replace('var bbsGlobal = ', '').replace(';', '')
    user_dict = json.decode(bbsGlobalDict)
    totalPage = user_dict['totalPage']
    return totalPage



url="http://bbs.tianya.cn/m/post-16-1667691-216.shtml"
bsSoup = getBsSoup(url)
pageTotal = getPageTotal(bsSoup)
print pageTotal
nowPage = 215
#for page in range(nowPage,pageTotal+1):
#    print page
floorContentmap =  getTiantaPageContent(bsSoup)
print floorContentmap['floorID']
#print floorContentmap['pageContent']
#print pageTotal
# print len(pageContent)