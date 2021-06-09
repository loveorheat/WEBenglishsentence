import numpy as np
import re
import json
import requests
import os
import time
import calendar
import exifread
from lxml import etree
from bs4 import BeautifulSoup
from urllib import parse
import urllib.request
#转换经纬度格式
def latitude_and_longitude_convert_to_decimal_system(*arg):
    """
    经纬度转为小数, param arg:
    :return: 十进制小数
    """
    return float(arg[0]) + ((float(arg[1]) + (float(arg[2].split('/')[0]) / float(arg[2].split('/')[-1]) / 60)) / 60)
#读取照片的GPS经纬度信息
def find_GPS_image(pic_path):
    GPS = {}
    date = ''
    with open(pic_path, 'rb') as f:
        tags = exifread.process_file(f)
        for tag, value in tags.items():
            #纬度
            if re.match('GPS GPSLatitudeRef', tag):
                GPS['GPSLatitudeRef'] = str(value)
            #经度
            elif re.match('GPS GPSLongitudeRef', tag):
                GPS['GPSLongitudeRef'] = str(value)
            #海拔
            elif re.match('GPS GPSAltitudeRef', tag):
                GPS['GPSAltitudeRef'] = str(value)
            elif re.match('GPS GPSLatitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                    GPS['GPSLatitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLatitude'] = latitude_and_longitude_convert_to_decimal_system(deg, min, sec)
            elif re.match('GPS GPSLongitude', tag):
                try:
                    match_result = re.match('\[(\w*),(\w*),(\w.*)/(\w.*)\]', str(value)).groups()
                    GPS['GPSLongitude'] = int(match_result[0]), int(match_result[1]), int(match_result[2])
                except:
                    deg, min, sec = [x.replace(' ', '') for x in str(value)[1:-1].split(',')]
                    GPS['GPSLongitude'] = latitude_and_longitude_convert_to_decimal_system(deg, min, sec)
            elif re.match('GPS GPSAltitude', tag):
                GPS['GPSAltitude'] = str(value)
            elif re.match('.*Date.*', tag):
                date = str(value)
    return {'GPS_information': GPS, 'date_information': date}
#通过baidu Map的API将GPS信息转换成地址。
def find_address_from_GPS(GPS):
    """
    使用Geocoding API把经纬度坐标转换为结构化地址。
    :param GPS:
    :return:
    """
    secret_key = 'zbLsuDDL4CS2U0M4KezOZZbGUY9iWtVf'
    if not GPS['GPS_information']:
        return '该照片无GPS信息'
    lat, lng = GPS['GPS_information']['GPSLatitude'], GPS['GPS_information']['GPSLongitude']
    baidu_map_api = "http://api.map.baidu.com/geocoder/v2/?ak={0}&callback=renderReverse&location={1},{2}s&output=json&pois=0".format(
        secret_key, lat, lng)
    response = requests.get(baidu_map_api)
    content = response.text.replace("renderReverse&&renderReverse(", "")[:-1]
    #print(content)
    baidu_map_address = json.loads(content)
    formatted_address = baidu_map_address["result"]["formatted_address"]
    province = baidu_map_address["result"]["addressComponent"]["province"]
    city = baidu_map_address["result"]["addressComponent"]["city"]
    district = baidu_map_address["result"]["addressComponent"]["district"]
    location = baidu_map_address["result"]["sematic_description"]
    return formatted_address,province,city,district,location
def show_img_address(path):
    GPS_info = find_GPS_image(path)
    address = find_address_from_GPS(GPS_info)
    return GPS_info.get("date_information"),str(address)
def get_calendar(year,month):
    year = int(year)
    month = int(month)
    num_zero = calendar.monthrange(year,month)[0]+1
    d = calendar.monthrange(year,month)[1]
    zero = np.zeros(num_zero).astype('int32')
    days =np.arange(1,d+1)
    beforelist = np.hstack((zero,days))
    num_zero1 = 42-len(beforelist)
    if num_zero1!=0:
        zero1 = np.zeros(num_zero1).astype('int32')
        endlist = np.hstack((beforelist,zero1))
        endlist = endlist.reshape(6,7)
    else:
        endlist = beforelist.reshape(6,7)
    return endlist
def distance_days_from(year,month,day):
    thisyear=time.strftime("%Y", time.localtime())
    thismonth =time.strftime("%m", time.localtime())
    thisday = time.strftime("%d", time.localtime())
    wholeday = 0
    if int(year)==int(thisyear) and int(month)==int(thismonth):
        wholeday =int(day)-int(thisday)
        if wholeday==0:
            wholeday = '祝考试顺利!'
        elif wholeday < 0:
            wholeday = '已结束'
        else:
            wholeday=wholeday
    if int(year)==int(thisyear) and int(month)>int(thismonth):
        for m in range(int(thismonth),int(month)):
            wholeday +=calendar.monthrange(int(year),m)[1]
        wholeday = wholeday+int(day)-int(thisday)
    return wholeday
