# -*- coding: utf-8 -*-
# @Time    : 2017/2/17 17:03
# @Author  : stephenfeng
# @Software: PyCharm Community Edition

import sys
reload(sys)
sys.setdefaultencoding('gbk')

import pandas as pd
import re

df = pd.read_csv('friend2.csv')


def city():
    '''微信朋友圈的城市'''
    address = df['city'].value_counts()
    print address


def gender():
    '''微信朋友的性别比例
        1:男  2：女   3：未知
    '''
    gender = df['male'].value_counts()
    print gender


def star():
    '''星标好友
        1:星标   0：非星标
    '''
    star = df['star'].value_counts()
    print star


def remark():
    remark = df['remark']
    name = df['name']

    remarkCount = 0
    maleCount = 0
    femaleCount = 0
    for i in range(1, len(remark)):
        if str(remark[i]).strip() == str(name[i]).strip() or remark[i] == '  noremark  ':
            remarkCount = remarkCount + 1
        else:
            if judgeGender(i) == 'male':
                maleCount = maleCount + 1
            elif judgeGender(i) == 'female':
                femaleCount = femaleCount + 1
    print '微信总朋友人数：', str(len(remark)), '\n'
    print '预计认识的总人数：', str(len(remark) - remarkCount), '\n'
    print '认识的人中汉子人数：', maleCount, '妹子人数：', femaleCount


def judgeGender(index):
    '''判断传入的某个位置的用户的性别
        参数：int行
        返回结果：字符串
    '''
    gender = df['gender']
    if gender[index] == '1':
        return 'male'
    elif gender[index] == '2':
        return 'female'
    else:
        return 'unknown'

def count_locate():
    '统计好友的位置信息'
    address = df['city'].value_counts()
    address = pd.DataFrame([address.index,address]).T
    #print address

    #匹配中文字符  一个中文占3个字符

    #好友全国各省份分布
    pat = re.compile('[\x80-\xff]')
    count_province = {}
    # for i in range(len(address[0])):
    #     loc = address[0].ix[i].strip()
    #     if re.match(pat, loc): #如果是中文地址
    #         province = loc[:5].strip() #提取省份出来
    #         count_province.setdefault(province, 0)
    #         count_province[province] += address[1].ix[i]  #相同省份的数量相加
    # for m,n in count_province.iteritems():
    #     print m.decode('gbk'), n
    # data = pd.Series(count_province)
    # data = pd.DataFrame([data.index, data.values]).T
    # print data
    # data.to_csv('province.csv', index=False, header=['地区','人数'])

    #省内好友各市分布
    for i in range(len(address[0])):
        loc = address[0].ix[i].strip()
        if re.match(pat, loc):  # 如果是中文地址
            province = loc[:5].strip()  # 提取省份出来
            if province.decode('gbk').encode('utf-8') == '广东': #如果是广东省的
                if len(loc.split()) != 1:
                    city = loc.split()[1]
                    #print city.decode('gbk').encode('utf-8')
                    count_province.setdefault(city, 0)
                    count_province[city] += address[1].ix[i]  # 相同省份的数量相加

    # for m, n in count_province.iteritems():
    #     print m.decode('gbk'), n
    data = pd.Series(count_province)
    data = pd.DataFrame([data.index, data.values]).T
    # print data
    data.to_csv('gaungdong_city.csv', index=False, header=[u'地区', u'人数'])

# if __name__ == '__main__':
#     remark()

city()
gender()
star()
count_locate()

