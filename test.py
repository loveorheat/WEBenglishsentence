from flask import Flask,abort, redirect, url_for,flash,request,render_template
import os
import urllib
import requests
import huzhiwen
import json
import time
import calendar
import numpy as np
from werkzeug.utils import secure_filename
ALLOWED_EXTENSIONS = {'png','jpg','jpeg'}
app = Flask(__name__)
app.config['SECRET_KEY'] = '123456'
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS
def qingyunke(msg):
    re = urllib.parse.quote(msg)
    url = 'http://api.qingyunke.com/api.php?key=free&appid=0&msg={}'.format(re)
    html = requests.get(url)
    return html.json()["content"]
def hello(word):
    return qingyunke(word)  
def EnglishSentence(year=2021,month=6,day=1):
    thisday=year+'-'+month+'-'+day
    n=0
    with open('../English/EnglishSentence.json', 'r', encoding='UTF-8') as file:
         EnglishSentences = json.loads(file.read())
    for i,sentence in enumerate(EnglishSentences):
        if sentence['Time']==thisday:
            n=i
    return EnglishSentences[n]
def School_information(choiceposition,choiceType):
    #筛选信息
    result = []
    with open('../English/schoolinformation.json', 'r', encoding='UTF-8') as file:
         schoolinformation = json.loads(file.read())
    for school in schoolinformation:
        if school["school_position"]==choiceposition and school["school_characteristics"]==choiceType:
            result.append(school)
        if choiceposition=='全部' and school["school_characteristics"]==choiceType:
            result.append(school)
    return result
@app.route('/',methods=['POST','GET'])
def login():
    if request.method == 'POST':
        if request.form['name']=='dragon' and request.form['pwd']=='huzhiwen1225':
            return redirect(url_for('index'))
    return render_template('login.html')
@app.route('/index',methods=['POST','GET'])
def index(photo_time="",photo_address="",content="content02"):
    get_content = request.args.get('content', '')
    if get_content!='':
        content = get_content
    school_Type = ['――','211','211985']
    choiceposition='全部'
    choiceType='――'
    get_choice_pos = request.args.get('position', '')
    if get_choice_pos!='':
        choiceposition = get_choice_pos
    get_choice_type = request.args.get('Type', '')
    if get_choice_type!='':
        choiceType=get_choice_type
    nature=School_information(choiceposition,choiceType)
    #页面渲染
    school_position = ['北京', '天津', '河北', '山西', '内蒙古', '辽宁', '吉林', '黑龙江', '上海', '江苏', '浙江', '安徽', '福建', '江西', '山东', '河南', '湖北', '湖南', '广东', '广西', '海南', '重庆', '四川', '贵州', '云南', '西藏', '陕西', '甘肃', '青海', '宁夏', '新疆', '香港', '澳门', '台湾', '全部']
    photo_time = request.args.get('photo_time', '')
    photo_address = request.args.get('photo_address', '')
    words = '求求你跟我聊天吧！'
    year=time.strftime("%Y", time.localtime())
    month = time.strftime("%m", time.localtime())
    changemonth = request.args.get('month', '')
    if changemonth!='':
        month = changemonth
    day = time.strftime("%d", time.localtime())
    calenders = huzhiwen.get_calendar(year,month)
    distance_days_frompostgraduate = huzhiwen.distance_days_from('2021','12','26')
    distance_days_fromCET = huzhiwen.distance_days_from('2021','6','12')
    changeday = request.args.get('day', '')
    if changeday!='':
        if int(changeday)<10:
            changeday = '0'+changeday
            day = changeday
        else:
            day = changeday
    sentence=EnglishSentence(year,month,day)
    choicemp3 = year+'-'+month+'-'+day+'.mp3'
    day = int(day)
    if request.method == 'POST':
        word = request.form['words']
        words = hello(word)
    AllMonth = ["01","02","03","04","05","06","07","08","09","10","11","12"]
    return render_template('index.html',name=words,sentence=sentence,calenders=calenders,thisday = day,distancepost = distance_days_frompostgraduate,distanceCET=distance_days_fromCET,AllMonth=AllMonth,thismonth=month,photo_time=photo_time,photo_address=photo_address,choicemp3=choicemp3,school_Type=school_Type,school_position=school_position,choiceposition=choiceposition,choiceType=choiceType,nature=nature,content=content)
@app.route('/photos', methods=['GET', 'POST'])
def photos_address():
    if request.method == 'POST':
        f = request.files.get('photo')
        content = request.form['content']
        if f.filename == '':
            flash('No selected file')
            print('No selected file')
            return redirect('inxex')
        if f and allowed_file(f.filename):
            print(allowed_file(f.filename))
            path = './'+"gps"+secure_filename(f.filename)
            f.save(path)
            try:
                photo_time,photo_address =huzhiwen.show_img_address(path)
            except Exception as e:
                return redirect(url_for('index',photo_time="照片格式错误",photo_address="照片格式错误",content=content))
            os.remove(path)
            return redirect(url_for('index',photo_time=photo_time,photo_address=photo_address,content=content))