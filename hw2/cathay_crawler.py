import os

import re
import pymysql
import requests
# from lxml import etree
from datetime import datetime
from bs4 import BeautifulSoup

class crawler_house():
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'
            }
        self.url_txt = './url_list.txt'
        self.crawler_url = 'https://rent.591.com.tw/?kind=0'
        self.city_list = ['1', '3'] # 台北市=1、新北市=3
        self.output_datetime_format = '%Y-%m-%d %H:%M:%S'
        self.db_settings = {
            'host': '0.0.0.0',
            'port': 3306,
            'user': 'root',
            'password': '********',
            'db': 'db_kai',
            'charset': 'utf8'
        }
    
    def find_items_url(self):
        url_list_tmp = []
        for i in self.city_list:
            cookies = {'urlJumpIp' : i} # 縣市的選擇是由cookies控制
            res = requests.get(self.crawler_url, headers=self.headers, cookies=cookies)
            html = BeautifulSoup(res.text, 'html.parser')
            last_page = html.find_all('a', {'class':'pageNum-form'})[-1].string # 獲取最後一頁的頁碼
            print('Total have ' + last_page + ' in region ' + i)
            
            for n in range(int(last_page)):
                item_num = n * 30 # 每一頁固定為30筆租屋物件
                page_url = self.crawler_url + '&firstRow=' + str(item_num)
                # https://rent.591.com.tw/?kind=0&firstRow=
                res = requests.get(page_url, headers=self.headers, cookies=cookies)
                html = BeautifulSoup(res.text, 'html.parser')
                # 獲取租屋物件的url
                for h in html.find_all('li', {'class':'pull-left infoContent'}):
                    url = h.select_one('a').get('href')
                    final_url = 'https:'+ url
                    url_list_tmp.append(final_url)
                print('page ' + str(n+1) + '/'+ last_page + ' url append done')
        
        # 去除重複的url
        url_list = list(set(url_list_tmp))
        # 紀錄url，用來比較每日差異
        with open(self.url_txt, 'w') as f:
            for url in url_list:
                f.write(url + '\n')

        return url_list

    def extract_items_info(self, url):
        landlord_name = 'NULL'
        landlord = 'NULL'
        phone_num = 'NULL'
        room_type = 'NULL'
        room_status = 'NULL'
        gender_type = 'NULL'
        city_name = 'NULL'

        res = requests.get(url, headers=self.headers)
        html = BeautifulSoup(res.text, 'html.parser')
        try:
            # 出租者
            landlord_name = html.select('div.avatarRight div i')[0].text
            # 出租者身份
            # res2 = requests.get(url, headers=self.headers).content
            # selector = etree.HTML(res2)
            # landlord_xpath = selector.xpath('/html/body/div[3]/div[3]/div[2]/div[2]/div[2]/div[1]/div[2]/div/text()')[0]
            landlord_select = html.select('div.avatarRight div')[0].text
            r = re.compile('屋主|代理人|仲介')
            landlord = r.findall(landlord_select)[0]
            # 連絡電話
            phone_num = html.select('span.dialPhoneNum')[0]['data-value']
            if phone_num == '':
                phone_num = html.select('div.hidtel')[0].text
                
            # 型態 & 現況
            room_info = html.find('ul', {'class':'attr'}).findAll('li')
            for info in room_info:
                if info.text.split('\xa0:\xa0\xa0')[0] == '型態':
                    room_type = info.text.split('\xa0:\xa0\xa0')[1]
                elif info.text.split('\xa0:\xa0\xa0')[0] == '現況':
                    room_status = info.text.split('\xa0:\xa0\xa0')[1]
            # 性別要求
            room_des = html.find('li',{'class':'clearfix'}).findAll('div')
            for des in room_des:
                r = re.compile('男生|女生|男女生皆可')
                if r.findall(des.text) != []:
                    gender_type = des.text.split('：')[-1]

            # 物件編號 (primary key)
            item_num = url.split('/')[-1].split('.')[0]
            # 爬蟲時間
            crawler_datetime = datetime.now().strftime(self.output_datetime_format)
            # 區域
            city_name = html.select('div#propNav.clearfix a')[2].text

            info_dict = {
                'item_num':item_num,
                'city_name': city_name,
                'landlord_name':landlord_name,
                'landlord':landlord,
                'phone_num':phone_num,
                'room_type':room_type,
                'room_status':room_status,
                'gender_type':gender_type,
                'crawler_datetime':crawler_datetime
            }

            return info_dict

        except Exception as e:
            print('crawler had some error: ', e)
            return False
        
    def main(self):
        ytd_url_list = []
        if os.path.isfile(self.url_txt):
            with open(self.url_txt, 'r') as f:
                for line in f.readlines():
                    ytd_url_list.append(line.strip())
        else:
            ytd_url_list = []

        url_list = self.find_items_url()
        
        # 資料源更新機制，比對與昨日的差異，決定今日需爬蟲的url
        td_url_set = set(url_list)
        ytd_url_set = set(ytd_url_list)
        url_add_today = list(td_url_set.difference(ytd_url_set))

        print('today need to handle : ', url_add_today)

        conn = pymysql.connect(**self.db_settings)
        cursor = conn.cursor()
        
        for url in url_add_today:
            print(url)
            info_dict = self.extract_items_info(url)
            if info_dict != False:
                info_value = tuple(info_dict.values())
                print(info_dict)
                sql = f'INSERT INTO rent_house_info VALUES {info_value};'
                print(sql)
                try:
                    cursor.execute(sql)
                    conn.commit()
                except Exception as e:
                    print('save in db had some error :', e)
            else:
                print(url + ' had some error, please check')

        cursor.close()
        conn.close()
            
if __name__ == '__main__':
    house_obj = crawler_house()
    house_obj.main()


