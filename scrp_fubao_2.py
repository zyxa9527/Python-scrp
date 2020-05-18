import os
import sys
import time
import datetime


from dateutil.parser import parse
from dateutil import parser


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from YUSCO.Util.account_parm import web_account_dic
import selenium.webdriver.support.ui as ui
from YUSCO.Scrapy.scrp_mariaDB import db_process
def web_info_collect(driver, arg_tar, arg_dics):
    driver.get(arg_dics['link'])
    table = driver.find_element_by_xpath('//*[@id="#"]/div/table')
    tddata = []
    for tr in table.find_elements_by_xpath('//tr'):
        tddata.append([td.text for td in tr.find_elements_by_xpath('td')])
    print('tddata'+str(tddata))
    
    price = []
    if len(tddata) > 0:
        if arg_tar == 'fubao01':
            p = trt_fubaol01(tddata)
        else:
            p = []
        
        if len(p) > 0:
            price += p

    return price
def trt_fubaol01(arg_data):
    global err_log
    global err_flag

    p_all = []
    for data in arg_data:
        if data[0] == '一级碳钢废钢':
            grp_code = '04001'
        else:
            grp_code = ''
            
        if len(grp_code) > 0 and data[5] != '停收' and float(data[5]) > 0:
            #print(data)
            data[5] = int(data[5])
            data[5] =str(data[5]*1.13)
            p = [grp_code, today_02, data[5]]
            p_all.append(p)

    if len(p_all) == 0:
        err_flag = True
        print('trt_fubaol01 資料異常:' + str(arg_data))
        err_log.write('trt_fubaol01 資料異常:' + str(arg_data) + '\n')

    return p_all

def info_fubao():
    global today,today_02,driver
    global err_log
    global err_flag
    err_flag = False

    log_name = "scrp_fubao_" + datetime.datetime.now().strftime("%Y%m%d") + ".txt"
    err_log = open(log_name, 'a', encoding = 'UTF-8')

    acc = web_account_dic('fubao_acc')
    pwd = web_account_dic('fubao_pwd')
    #print(acc)
    #print(pwd)

    chrome_options = Options()
    driver = webdriver.Chrome(chrome_options=chrome_options)  
    #driver.implicitly_wait(5)

    today = str(datetime.datetime.now())
    today_02 = today[0:4] + str(int(today[5:7])) + str(int(today[8:10]))
    print(today_02)
    driver.get('http://www.f139.com/') 

    elem=driver.find_element_by_id("userName")
    elem.send_keys(acc)
    elem=driver.find_element_by_id("passWord")
    elem.send_keys(pwd)
    elem=driver.find_element_by_xpath('//*[@id="loginForm"]/input[6]')
    elem.click()

    try:
        elem = driver.find_element_by_xpath('//*[@id="loginerror"]')
        if len(elem.text) > 0:
            err_flag = True
            print("網站登入異常，error msg:")
            print(elem.text)
            err_log.write("網站登入異常，error msg:")
            err_log.write(elem.text)
    except:
        print("網站正常登入.")


    if err_flag == False:
            #Target website arguments dict
            tar_args_dic = {
                'fubao01': {'link': 'http://data.f139.com/list.do?pid=&vid=84&qw=5:231'},     
            }

            #執行各項報表抓取
            price_all = []
            for tar, url in tar_args_dic.items():
                print('開始進行 ' + tar + ' 資料抓取.' )
                err_log.write('\n\n開始進行 ' + tar + ' 資料抓取.\n' )

                try:
                    price = web_info_collect(driver, tar, url)
                    err_log.write(str(price) + '\n')
                    print('price'+str(price))

                    if len(price) > 0:
                        price_all += price
    
                    err_log.write('來源 ' + tar + ' 資料抓取完畢.\n' )
                    print('price_all'+str(price_all))
                    if len(price_all) > 0:
                        #print(price_all)
                        result=db_process(price_all)
                        err_flag = result[0]
                        err_log.write(result[1])
                        print(result)

                    err_log.write(str(price) + '\n')
                    err_log.write('來源 ' + tar + ' 資料抓取完畢.\n' )

                except Exception as e:
                    err_flag = True
                    print("info_fubao -> " + tar + " 資料抓取錯誤，例外訊息如下:")
                    print(e.args)
                    print("\n\n")
                    err_log.write("info_fubao -> " + tar + " 資料抓取錯誤，例外訊息如下:\n")
                    err_log.write(str(e.args))
                    err_log.write("\n\n")


    #關閉瀏覽器視窗
    driver.quit()
    # Close File
    err_log.close()    
    
if __name__ == '__main__':
    info_fubao()
