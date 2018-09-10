#coding=utf-8
import logging
from logging.handlers import RotatingFileHandler
import sys
import urllib2

import demjson
import json
from bs4 import BeautifulSoup


log_file = "./logs/GetNovel.log"

logger = logging.getLogger()
logger.setLevel('INFO')        # 日志级别
BASIC_FORMAT = "[%(asctime)s][%(filename)s line:%(lineno)d][%(levelname)s]: %(message)s"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
formatter = logging.Formatter(BASIC_FORMAT, DATE_FORMAT)
chlr = logging.StreamHandler() # 输出到控制台的handler
chlr.setFormatter(formatter)
fhlr = RotatingFileHandler(log_file,"a",10240,5) # 输出到文件的handler
fhlr.setFormatter(formatter)
logger.addHandler(chlr)
logger.addHandler(fhlr)


def getBsSoup(url):
    """
    获取bssoup对象
    """
    try:
        htmlContent = urllib2.urlopen(url)
    except urllib2.HTTPError as e:
        logger.error('get url content failed : ' + str(e.code))
        sys.exit()
    except urllib2.URLError as e:
        logger.error('get url content failed : ' + str(e.reason))
        sys.exit()
    soup = BeautifulSoup(htmlContent, "lxml")
    return soup



def  getTiantaPageContent(bsSoup):
    """
    匹配天涯移动版 莲蓬鬼话 板块 帖子<<没有名字的人 >>
    传入每页地址，返回回复是楼主的楼层内容
    """
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


def getPageTotal(bsSoup):
    """
    返回当前帖子总页数
    """
    bbsGlobalDict = bsSoup.script.contents[0].string.replace('var bbsGlobal = ', '').replace(';', '')
    user_dict = demjson.decode(bbsGlobalDict)
    totalPage = user_dict['totalPage']
    return totalPage


def getUpdatePage(webUrl,databaseFile):
    """
    从文件读取上次保存的最后页面和最后楼层
    """

    with open(databaseFile,'r') as load_f:
        pageinfo_dict = json.load(load_f)
        nowpage = str(pageinfo_dict['currentPage'])
        #nowpage = "336"
        #nowFloorID = str(pageinfo_dict['currentPageFloorID'])

    nowUrl = webUrl.replace('{PG}',nowpage)
    bsSoup = getBsSoup(nowUrl)
    finalPage = getPageTotal(bsSoup)
    floorID = getTiantaPageContent(bsSoup)['floorID']
    finalUrl = webUrl.replace('{PG}',str(finalPage))
    bsSoupFinal = getBsSoup(finalUrl)
    finalFloorID = getTiantaPageContent(bsSoupFinal)['floorID']

    logger.debug("finalPage:%s",str(finalPage))
    logger.debug("floorID:%s",str(floorID))
    logger.debug("finalFloorID:%s",str(finalFloorID))

    pageContentStrList = []
    ###TODO ： 这里只判断了页码，未判断楼层，待补充
    if int(finalPage) == int(nowpage) :
        logger.info("网页内容未更新, 当前页数[%s]，总页数[%s] .",str(nowpage),str(finalPage))
        return ""
    elif int(finalPage) < int(nowpage) :
        logger.error("网页内容页数记录异常, 当前页数[%s]，总页数[%s] .",str(nowpage),str(finalPage))
        return ""
    else:
        logger.info("网页内容已更新, 当前页数[%s]，总页数[%s] .", str(nowpage), str(finalPage))
        for page in range(int(nowpage), int(finalPage)+1) :
            logger.info("内容抓取中, 当前页数[%s]，总页数[%s] .", str(page), str(finalPage))
            dealUrl = webUrl.replace('{PG}',str(page))
            logger.debug("nowUrl:%s", str(dealUrl))
            pageSoup = getBsSoup(dealUrl)
            pageContent = getTiantaPageContent(pageSoup)['pageContent'].encode('utf-8').strip()
            #pageContent = getTiantaPageContent(pageSoup)['pageContent'].strip()
            if pageContent != "" :
                pageContentStrList.append('<p>' + pageContent + '</p>')

    #将当前已读的最后一页和楼层写入文件保存
    pageinfo_dict['currentPage'] = str(finalPage)
    pageinfo_dict['currentPageFloorID'] = str(finalFloorID)
    with open(databaseFile,"w") as f:
        json.dump(pageinfo_dict,f)

    #返回页面更新的内容
    if pageContentStrList :
        pageContentStr = '\n'.join(pageContentStrList)
        #pageContentStrHtml = '<html5><p>源网页: '.encode('utf-8') + nowUrl.encode('utf-8') + '</p>'.encode('utf-8') + pageContentStr + '\n'.encode('utf-8') + '<p>源网页: '.encode('utf-8') + nowUrl.encode('utf-8') + '</p></html5>'.encode('utf-8')
        pageContentStrHtml = "<html5><img src='https://uploadbeta.com/api/pictures/random/' style='max-width:100%'><p><a href=" + nowUrl + ">点击查看源网页</a></p>" + pageContentStr + "<p><a href=" + nowUrl + ">点击查看源网页</a></p>" + "<p><img src='https://uploadbeta.com/api/pictures/random/?key=BingEverydayWallpaperPicture' style='max-width:100%'></p>" + "</html5>"
        return pageContentStrHtml
    else:
        return ""

#=========================================
#格式化email的头部信息，不然会出错，当做垃圾邮件
#=========================================
def _format_addr(s):
    from email.utils import parseaddr, formataddr
    from email.header import Header

    name, addr = parseaddr(s)
    return formataddr((Header(name, 'utf-8').encode(), addr))


def sendmail(receivers,mailtitle,mailcontent):
    """
    发送邮件
    """
    import smtplib
    from email.mime.text import MIMEText

    ret = True
    sender = "imleixi@live.com"
    mail_host = "smtp-mail.outlook.com"  # 设置服务器
    mail_user = "imleixi@live.com"  # 用户名
    mail_pass = "letmeinMICROSOFT001"  # 口令
    mail_port = 587 # stmp服务器端口

    try:
        msg = MIMEText(mailcontent, 'html', 'utf-8')
        msg['Subject']=mailtitle                # 邮件的主题，也可以说是标题
        msg['to'] = _format_addr(','.join(receivers))

        server=smtplib.SMTP(mail_host, mail_port)  # 发件人邮箱中的SMTP服务器
        server.ehlo()  # 向服务器发送SMTP 'ehlo' 命令
        server.starttls()
        server.login(mail_user, mail_pass)  # 发件人邮箱账号、邮箱密码
        server.sendmail(sender,receivers,msg.as_string())  # 发件人邮箱账号、收件人邮箱账号、发送邮件
        server.quit()# 关闭连接
    except Exception as e:
        print (e)
        ret=False
    return ret


##### Main ####
#网页内容<没有名字的人> 地址
webUrl = 'http://bbs.tianya.cn/m/post-16-1667691-{PG}.shtml'
databaseFile = './database.json'

pageContentStr = getUpdatePage(webUrl,databaseFile)
if pageContentStr == "":
    logger.info("网页未更新.")
else:
    logger.info("网页已更新.")

    receivers = ['leixichina@live.com']
    mailtitle = '天涯<没有名字的人>更新推送'
    mailcontent = pageContentStr


    res = sendmail(receivers,mailtitle,mailcontent)
    if res:
        logger.info("更新通知邮件发送成功! 收件人列表:%s",receivers)
    else:
        logger.error("更新通知邮件发送失败！")
