# -*- coding: utf-8 -*-
"""
長江有色金屬網現貨#1鎳 報價資料收集

說明:
    來源：長江有色金屬網

    info_ccmn(): 主要模組，進行登入網站，並呼叫其他抓取報表程序
    scrp_ccmn01(): 爬取網頁資料

    代碼
    '11001': 長江有色金屬網現貨#1鎳

    PS:
    ccmn 網站切換headless模式，會出現資料擷取長度不足問題，保留開視窗設定.

"""
#General import
import os
import time
import re
import datetime
import mysql.connector

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

#custom import
from YUSCO.Scrapy.scrp_mariaDB import db_process2

def scrp_ccmn01(driver):
    driver.get("https://www.ccmn.cn/")

    #讀取內文報價資料
    tr_elem = driver.find_element_by_xpath('//*[@id="quoPrice_box"]/table')
    for tr in tr_elem.find_elements_by_xpath('//tr'):
        ls = [td.text for td in tr.find_elements_by_xpath('td   ') if len(td.text.strip()) > 0]
        #print(ls)
        if (len(ls) > 0) and ('1#镍' in ls[0]):
            break

    price = []
    if len(ls) > 0:
        #價格區間 
        print(ls)
        lo_hi = ls[1].split('—')

        #資料日期
        raw_dt = ls[-1]
        yyyy = datetime.datetime.now().strftime("%Y")
        d = yyyy + '-' + raw_dt
        d = datetime.datetime.strptime(d, '%Y-%m-%d')
        data_date = d.strftime('%Y%m%d')

        price.append(['11001', data_date] + [ls[2]] + lo_hi)

    return price

def info_ccmn():
    global err_log
    global err_flag
    err_flag = False

    print("Executing " + os.path.basename(__file__) + "...")
    print("Current datetime " + str(datetime.datetime.now()))
    print('開始 長江有色金屬網現貨#1鎳 報價資料收集程序...')

    #LOG File
    log_name = "scrp_ccmn_" + datetime.datetime.now().strftime("%Y%m%d") + ".txt"
    err_log = open(log_name, 'a', encoding = 'UTF-8')

    tStart = time.time()#計時開始
    err_log.write("\n\n\n*** LOG datetime  " + str(datetime.datetime.now()) + " ***\n")
    err_log.write("Executing " + os.path.basename(__file__) + "...\n\n")

    chrome_options = Options()
    #chrome_options.add_argument('--headless')
    #chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=chrome_options)

    price = []
    #讀取~1美元對新台幣即期賣出價
    try:
        price = scrp_ccmn01(driver)
        print(price)
    except Exception as e:
        err_flag = True
        print("info_ccmn -> scrp_ccmn01 資料抓取錯誤，例外訊息如下:")
        print(e.args)
        print("\n\n")
        err_log.write("info_ccmn -> scrp_ccmn01 資料抓取錯誤，例外訊息如下:\n")
        err_log.write(str(e.args))
        err_log.write("\n\n")

    #關閉瀏覽器視窗
    driver.quit()

    #寫入資料庫
    if len(price) > 0:
        #print(price)
        db_process2(price)

    tEnd = time.time()#計時結束
    err_log.write ("\n\n\n結轉耗時 %f sec\n" % (tEnd - tStart)) #會自動做進位
    err_log.write("*** End LOG ***\n\n")

    # Close File
    err_log.close()

    #如果執行過程無錯誤，最後刪除log file
    if err_flag == False:
        os.remove(log_name)

    print('\n\n\n本次 長江有色金屬網現貨#1鎳 市場報價資訊抓取結束，等待下次執行...\n\n\n')

if __name__ == '__main__':
    info_ccmn()
