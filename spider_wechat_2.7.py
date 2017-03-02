# -*- coding: utf-8 -*-
# @Time    : 2017/2/16 13:17
# @Author  : stephenfeng
# @Software: PyCharm Community Edition

'''
pyhton2.7版本 爬取微信好友
'''

import requests
import ssl
import time
import re
import os
import sys
import ssl
import subprocess
import xml.dom.minidom
import json
import csv

#一些全局变量
DEBUG = False  # 测试时候 可以改为True，输出测试的json数据

QRImagePath = os.path.join(os.getcwd(), 'qrcode.jpg')  # 存放登录二维码的位置，不需要改

tip = 0
uuid = ''

base_uri = ''
redirect_uri = ''
push_uri = ''

skey = ''
wxsid = ''
wxuin = ''
pass_ticket = ''
deviceId = 'e000000000000000'

BaseRequest = {}

# #requests模块：发送带参数的get请求,将key与value放入一个字典中，通过params参数来传递,其作用相当于urllib.urlencode
# pqyload = {'q':'杨彦星'}
# r = requests.get('http://www.so.com/s',params = pqyload)
# print r.url

def responseState(func, BaseResponse):  #responseState('webwxinit', dic['BaseResponse'])
    ErrMsg = BaseResponse['ErrMsg']  # ""
    Ret = BaseResponse['Ret']  #0
    if DEBUG or Ret != 0:
        print('func: %s, Ret: %d, ErrMsg: %s' % (func, Ret, ErrMsg))

    if Ret != 0:
        return False

    return True  #当Ret == 0 时返回真

def getUUID():
    '获取uuid'
    global uuid  #全局变量uuid

    url = 'https://login.weixin.qq.com/jslogin'
    params = {
        'appid': 'wx782c26e4c19acffb',
        'fun': 'new',
        'lang': 'zh_CN',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)
    r.encoding = 'utf-8'
    data = r.text  #返回一个unicode字符串，其中包含window.QRLogin.uuid的值
    print '第一次get请求：'
    print 'uuid: ', r.url

    regx = r'window.QRLogin.code = (\d+); window.QRLogin.uuid = "(\S+?)"'
    pm = re.search(regx, data)
    code = pm.group(1)
    uuid = pm.group(2)

    if code == '200': #如果code值为200则说明连接成功 获取到正确的全局变量uuid
        return True
    return False

def showQRImage():
    '获取登录的二维码图片并显示出来'
    global tip  #全局变量tip

    url = 'https://login.weixin.qq.com/qrcode/' + uuid
    params = {
        't': 'webwx',
        '_': int(time.time()),
    }

    r = myRequests.get(url=url, params=params)
    print '\n第二次get请求：', r.url

    tip = 1  #全局变量tip设为1

    f = open(QRImagePath, 'wb')  #wb：写入一个二进制文件
    f.write(r.content)  #把生成的二维码图片写进文件
    f.close()
    time.sleep(1) #暂停一秒

    if sys.platform.find('darwin') >= 0:  # 'darwin' 如果当前操作平台是Mac OS X系统  等同于：sys.platform.startwith('darwin')
        subprocess.call(['open', QRImagePath])
    elif sys.platform.find('linux') >= 0: #Linux系统
        subprocess.call(['xdg-open', QRImagePath])
    else: #windows操作系统
        # os.startfile(path[, operation])使用其关联的应用程序启动文件。 path参数是相对于当前目录的。如果要使用绝对路径，请确保第一个字符不是斜杠（'/'）
        os.startfile(QRImagePath)  #打开该二维码图片

    print('请使用微信扫描二维码以登录')

def waitForLogin():
    global tip, base_uri, redirect_uri, push_uri  #申明这几个全局变量

    url = 'https://login.weixin.qq.com/cgi-bin/mmwebwx-bin/login?tip=%s&uuid=%s&_=%s' % (
        tip, uuid, int(time.time()))

    r = myRequests.get(url=url)
    r.encoding = 'utf-8'
    data = r.text
    print '\n第三次get请求：'
    print 'login_url: ', r.url


    regx = r'window.code=(\d+);'
    pm = re.search(regx, data)

    code = pm.group(1)

    if code == '201':  # 已扫描
        print('成功扫描,请在手机上点击确认以登录')
        print '请求获得的内容：', data
        tip = 0
    elif code == '200':  # 已登录
        print('\n正在登录...')
        print '请求获得的内容：', data
        print '\n'
        regx = r'window.redirect_uri="(\S+?)";'
        pm = re.search(regx, data)

        redirect_uri = pm.group(1) + '&fun=new'
        base_uri = redirect_uri[:redirect_uri.rfind('/')]
        print 'redirect_uri: ', redirect_uri
        print 'base_uri: ', base_uri
    elif code == '408':  # 超时
        pass
    # elif code == '400' or code == '500':

    #此时已经登记好base_uri, redirect_uri, push_uri
    return code  #返回此时request请求获取的状态码

def login():
    global skey, wxsid, wxuin, pass_ticket, BaseRequest

    r = myRequests.get(url=redirect_uri) #使用在waitForLogin()获取的redirect_uri 再次进行请求
    r.encoding = 'utf-8'
    data = r.text

    #print(data)

    doc = xml.dom.minidom.parseString(data)   #用xml.dom.minidom解析XML文档
    root = doc.documentElement
    #print root
    for node in root.childNodes:
        if node.nodeName == 'skey':
            skey = node.childNodes[0].data
        elif node.nodeName == 'wxsid':
            wxsid = node.childNodes[0].data
        elif node.nodeName == 'wxuin':
            wxuin = node.childNodes[0].data
        elif node.nodeName == 'pass_ticket':
            pass_ticket = node.childNodes[0].data

    # print('skey: %s, wxsid: %s, wxuin: %s, pass_ticket: %s' % (skey, wxsid,
    # wxuin, pass_ticket))

    if not all((skey, wxsid, wxuin, pass_ticket)): #如果都没有值
        return False

    BaseRequest = {
        'Uin': int(wxuin),
        'Sid': wxsid,
        'Skey': skey,
        'DeviceID': deviceId,
    }
    print '登录成功'
    print 'BaseRequest字典:', BaseRequest
    return True

def webwxinit():
    #URL中有webwxinit
    url = (base_uri +
           '/webwxinit?pass_ticket=%s&skey=%s&r=%s' % (
               pass_ticket, skey, int(time.time())))
    params = {'BaseRequest': BaseRequest}
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, data=json.dumps(params), headers=headers)
    r.encoding = 'utf-8'
    data = r.json()

    print '\n初始化URL:', url
    print data  #该data就是一系列json格式的数据

    if DEBUG:  #测试用 DEBUG设置为True可生成josn文件在本机查看
        f = open(os.path.join(os.getcwd(), 'webwxinit.json'), 'wb')
        f.write(r.content)
        f.close()

    # print(data)

    global ContactList, My, SyncKey
    dic = data
    ContactList = dic['ContactList']  #获取联系人
    My = dic['User']  #获取用户
    SyncKey = dic['SyncKey']

    state = responseState('webwxinit', dic['BaseResponse'])
    return state

def webwxgetcontact():
    '读取微信好友'
    #URL中有webwxgetcontact
    url = (base_uri +
           '/webwxgetcontact?pass_ticket=%s&skey=%s&r=%s' % (
               pass_ticket, skey, int(time.time())))
    headers = {'content-type': 'application/json; charset=UTF-8'}

    r = myRequests.post(url=url, headers=headers)
    r.encoding = 'utf-8'
    data = r.json()
    print '\n读取联系人URL: ', url
    print data
    if DEBUG:
        f = open(os.path.join(os.getcwd(), 'webwxgetcontact.json'), 'wb')
        f.write(r.content)
        f.close()

    dic = data  #data是json格式
    MemberList = dic['MemberList']  #获取联系人

    # 倒序遍历,不然删除的时候出问题..
    SpecialUsers = ["newsapp", "fmessage", "filehelper", "weibo", "qqmail", "tmessage", "qmessage", "qqsync",
                    "floatbottle", "lbsapp", "shakeapp", "medianote", "qqfriend", "readerapp", "blogapp", "facebookapp",
                    "masssendapp",
                    "meishiapp", "feedsapp", "voip", "blogappweixin", "weixin", "brandsessionholder", "weixinreminder",
                    "wxid_novlwrv3lqwv11", "gh_22b87fa7cb3c", "officialaccounts", "notification_messages", "wxitil",
                    "userexperience_alarm"]
    for i in range(len(MemberList) - 1, -1, -1): #倒叙遍历MemberList
        Member = MemberList[i]
        if Member['VerifyFlag'] & 8 != 0:  # 公众号/服务号
            MemberList.remove(Member)
        elif Member['UserName'] in SpecialUsers:  # 特殊账号
            MemberList.remove(Member)
        elif Member['UserName'].find('@@') != -1:  # 群聊
            MemberList.remove(Member)
        elif Member['UserName'] == My['UserName']:  # 自己
            MemberList.remove(Member)

    return MemberList

def main():
    global myRequests #设置一个myRequests全局变量
    #步骤1：建立全局request请求
    if hasattr(ssl, '_create_unverified_context'):  #判断ssl中是否有_create_unverified_context方法
        ssl._create_default_https_context = ssl._create_unverified_context

    #会话对象让你能够跨请求保持某些参数，最方便的是在同一个Session实例发出的所有请求之间保持cookies，且这些都是自动处理的
    headers = {
        'User-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.125 Safari/537.36'}
    myRequests = requests.Session()
    myRequests.headers.update(headers)
    #return myRequests

    #步骤2：请求获取uuid值
    if not getUUID():
        print('获取uuid失败')
        return

    #步骤3：请求获取登录二维码图片
    print('正在获取二维码图片...')
    showQRImage()

    #步骤4：手机扫码验证确认请求登录
    while waitForLogin() != '200':
        pass

    #移除二维码照片
    os.remove(QRImagePath)

    #步骤5：请求验证是否登陆成功
    print '\n'
    if not login():
        print('登录失败')
        return

    if not webwxinit():
        print('初始化失败')
        return

    MemberList = webwxgetcontact()
    print '\n所有好友资料:', MemberList

    MemberCount = len(MemberList)
    print('通讯录共%s位好友' % MemberCount)

    # import sys
    # reload(sys)
    # sys.setdefaultencoding('utf8')
    # f = open(os.path.join(os.getcwd(), 'My_contact.json'), 'wb')
    # f.write(json.dumps(MemberList, sort_keys=True, indent=2, ensure_ascii=False))
    # f.close()

    d = {}
    imageIndex = 0
    # 写入csv
    csvfile = open('friend2.csv', 'wb')  # csvfile.write(codecs.BOM_UTF8)
    writer = csv.writer(csvfile)
    writer.writerow(['name', 'city', 'male', 'star', 'signature', 'remark', 'alias', 'nick'])

    for Member in MemberList:
        global writer

        ##稍微处理下空字符串
        imageIndex = imageIndex + 1
        d[Member['UserName']] = (Member['NickName'], Member['RemarkName'])  # d为一个字典
        city = Member['City']
        city = 'nocity' if city == '' else  city
        name = Member['NickName']  # 有些昵称包含表情
        name = 'noname' if name == '' else  name.strip()
        sign = Member['Signature']
        sign = 'nosign' if sign == '' else  sign.strip()
        remark = Member['RemarkName']
        remark = 'noremark' if remark == '' else remark
        alias = Member['Alias']
        alias = 'noalias' if alias == '' else alias
        nick = Member['NickName']
        nick = 'nonick' if nick == '' else nick

        ##下载好友头像
        # name = os.getcwd() + '\\img\\' + str(imageIndex) + '.jpg'
        # imageUrl = 'https://wx2.qq.com' + Member['HeadImgUrl']  #图片的URL
        # r = myRequests.get(url=imageUrl, headers=headers)
        # imageContent = (r.content)
        # print name
        # print r.url
        # # print r.content
        # print '\n'
        # fileImage = open(name, 'wb')
        # fileImage.write(imageContent)
        # fileImage.close()
        # print('正在下载第：' + str(imageIndex) + '位好友头像')

        import sys
        reload(sys)
        sys.setdefaultencoding('utf-8')  #修改系统默认解码为utf-8
        # # 写入csv
        # #加上ignore参数，表示在编码和解码时，忽略掉那些无法编码和解码的字符
        # # 姓名、城市、性别、是否星标朋友、个人签名、备注、别名、个人昵称
        #
        # ##这是python3.5版本可以用的代码
        # # writer.writerow([name.encode('gbk', 'ignore').decode('gbk'),
        # #                  city.encode('gbk', 'ignore').decode('gbk'),
        # #                  Member['Sex'],
        # #                  Member['StarFriend'],
        # #                  sign.encode('gbk', 'ignore').decode('gbk'),
        # #                  remark.encode('gbk', 'ignore').decode('gbk'),
        # #                  alias.encode('gbk', 'ignore').decode('gbk'),
        # #                  nick.encode('gbk', 'ignore').decode('gbk')])  #unicode转gbk,gbk再转unicode
        #
        # ##python2.7版本可以用的代码
        writer.writerow([name.decode('utf-8').encode('gbk', 'ignore'),
                         city.decode('utf-8').encode('gbk', 'ignore'),
                         Member['Sex'],
                         Member['StarFriend'],
                         sign.decode('utf-8').encode('gbk', 'ignore'),
                         remark.decode('utf-8').encode('gbk', 'ignore'),
                         alias.decode('utf-8').encode('gbk', 'ignore'),
                         nick.decode('utf-8').encode('gbk', 'ignore')])  # unicode转gbk,gbk再转unicode
        print('正在保存第 %d 个好友 %s 的个人资料') % (imageIndex, str(remark))
        # # print(name, '  ^+*+^  ', city, '  ^+*+^  ', Member['Sex'], ' ^+*+^ ', Member['StarFriend'], ' ^+*+^ ', sign,
        # #       ' ^+*+^ ', remark, ' ^+*+^ ', alias, ' ^+*+^ ', nick)
    csvfile.close()


if __name__ == '__main__':
    main()
    print '好友资料加载完毕'