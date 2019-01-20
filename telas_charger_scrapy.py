#!/usr/bin/env python
# coding=utf-8
import xlwt
import requests
import re
#从Tesla的美国官网获得美国境内的的充电桩位置信息，再由地图导出经纬度信息
##获取网页的源代码

BASE_URL="https://www.tesla.com"
LIST_URL="https://www.tesla.com/findus/list"
#chargers or superchargers
CHARER_TYPE="chargers"
#这里需要自己结合网页上的地名修改
REGION="United+States"

filename=REGION+"./tesla_"+CHARER_TYPE+".xls"
region_url = LIST_URL+"/"+CHARER_TYPE+"/"+REGION

data_got = 0
data_error = 0

def get_one_page(url):
 try:
    headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ''Chrome/51.0.2704.63 Safari/537.36'}
    response = requests.get(url,headers = headers, timeout = 30)
    if response.status_code == 200:
        return response.text
    else:
        print(response.status_code)
        return None
 except:
    print('Requests Error')
    return None
#创建表格,添加工作表
book = xlwt.Workbook(encoding='utf-8',style_compression=0)
sheet = book.add_sheet('sheet1',cell_overwrite_ok=True)
#对网页源代码进行匹配

html_region = get_one_page(region_url)
##编译正则匹配对象(就是括号内的部分)
##re.S正则表达式修饰符:使 . 匹配包括换行在内的所有字符
pattern_sub_regions = re.compile('<address.*?<a.*?href="(.*?)".*?>(.*?)</a>.*?</address>',re.S)
##匹配所有的位置条目
suffix_sub_regions = re.findall(pattern_sub_regions,html_region)
#输出形如(/findus/location/charger/dc2789，Benson&#039;s Appliance Center)的tuple组成的list
#对匹配的位置条目查询器经纬度信息

for suffix_sub_region in suffix_sub_regions:
    sheet.write(data_got,0,suffix_sub_region[1])
    url_sub_region = BASE_URL+suffix_sub_region[0]
    html_sub_region = get_one_page(url_sub_region)
    pattern_location = re.compile('&center=(.*?)&zoom',re.S)
    if CHARER_TYPE=="superchargers":
        pattern_chargers = re.compile('<p><strong>[Cc]harging</strong>.*?>(.*?) [Ss]uperchargers.*?</p>',re.S)
    if CHARER_TYPE=="chargers":
        pattern_chargers = re.compile('<p><strong>[Cc]harging</strong>.*?>(.*?)Tesla.*?</p>',re.S)
    try:
        location = re.findall(pattern_location,html_sub_region) ##输出经纬度的list
        sheet.write(data_got,1,location[0])
    except:
        print('Error',data_error,':',url_sub_region)
        data_error+=1
    try:
        chargers = re.findall(pattern_chargers,html_sub_region) ##输出充电桩的个数
        sheet.write(data_got,2,chargers[0])
    except:
        chargers = ['0']
        sheet.write(data_got,2,'0')
    print(data_got,':',suffix_sub_region[1],location[0],chargers[0])
    data_got+=1

#直接把结果保存在当前目录下的xls文件里面
book.save(filename)
print('Finished,totally got %d Charging Station,and %d Error'% (data_got,data_error))
