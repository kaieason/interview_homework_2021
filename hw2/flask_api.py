# -*- coding: utf-8 -*-
import pymysql
from sqlalchemy import create_engine
from flask import Flask, render_template, jsonify, request

from for_sql import generate_sql_script

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
app.config['DEBUG'] = True
app.config['JSONIFY_MIMETYPE'] = 'application/json;charset=utf-8'

HOSTNAME = '0.0.0.0'
USER = 'root'
PASSWORD = '******'
DB = 'db_kai'

conn = create_engine(f"mysql+pymysql://{USER}:{PASSWORD}@{HOSTNAME}/{DB}")
cur = conn.connect()

@app.route('/')
def index():
    output_str = '請透過http://0.0.0.0:8001/search?city=0&landlord=1&ln=黃&fn=1&phone=[0989-230-091]&gender=1 調整參數做查詢'
    return output_str

@app.route("/search")
def get_cafe_at_location():
    try:
        # 取得查詢 連絡電話 的值
        select_phone = request.args.get("phone")
        # 取得查詢 性別要求 的值
        select_gender = request.args.get("gender")  
        if select_gender == '0':
            select_gender = '("男生")'
        elif select_gender == '1':
            select_gender = '("女生")'
        elif select_gender == '2':
            select_gender = '("男女生皆可")'
        elif select_gender == '3':
            select_gender = '("NULL")'
        elif select_gender == '4':
            select_gender = '("男生", "男女生皆可", "NULL")'
        elif select_gender == '5':
            select_gender = '("女生", "男女生皆可", "NULL")'
        # 取得查詢 出租者身份 的值
        select_landlord = request.args.get("landlord")
        if select_landlord == '0':
            select_landlord = '("屋主")'
        elif select_landlord == '1':
            select_landlord = '("仲介")'
        elif select_landlord == '2':
            select_landlord = '("代理人")'    
        elif select_landlord == '3':
            select_landlord = '("屋主", "仲介")'    
        elif select_landlord == '4':
            select_landlord = '("仲介", "代理人")'  
        elif select_landlord == '5':
            select_landlord = '("屋主", "代理人")'  
        # 取得查詢 縣市 的值
        select_city = request.args.get("city")
        if select_city == '0':
            select_city = '("台北市")'
        elif select_city == '1':
            select_city = '("新北市")'
        # 取得查詢 出租者姓氏 的值
        select_landlord_last_name = request.args.get("ln")
        if select_landlord_last_name != None:
            select_landlord_last_name = select_landlord_last_name.replace('"','')
            select_landlord_last_name = 'and landlord_name like "' + select_landlord_last_name + '%%"'
        # 取得查詢 出租者為男生或女生 的值
        select_landlord_first_name = request.args.get("fn")
        if select_landlord_first_name == '0':
            select_landlord_first_name = 'and (landlord_name like "%%先生%%" or landlord_name like "%%爸爸%%")' 
        elif select_landlord_first_name == '1':
            select_landlord_first_name = 'and (landlord_name like "%%小姐%%" or landlord_name like "%%小姊%%" or landlord_name like "%%阿姨%%" \
                or landlord_name like "%%太太%%" or landlord_name like "%%女士%%" or landlord_name like "%%媽媽%%")' 

        select_dict = {
            'city_name':select_city,
            'last_name':select_landlord_last_name,
            'first_name': select_landlord_first_name, 
            'landlord':select_landlord,
            'phone_num':select_phone,
            'gender_type':select_gender
        }
        # 產生查詢的sql
        sql = generate_sql_script(select_dict)

        results = cur.execute(sql)
        payload = []
        content = {}
        for result in results:
            content = {
                '物件編號': result[0],
                '縣市':result[1],
                '出租者': result[2], 
                '出租者身份': result[3], 
                '連絡電話': result[4], 
                '型態': result[5], 
                '現況': result[6], 
                '性別要求': result[7]
                }
            payload.append(content)
            content = {}

        return jsonify(payload), 200
    except:
        return jsonify(error={"Not Found": "Sorry, your API url had some error"}), 404

if __name__ == '__main__':
   app.run(host='0.0.0.0', port=8001, debug=True)