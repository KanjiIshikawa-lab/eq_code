import os
import eel
from selenium import webdriver
from selenium.webdriver import Chrome, ChromeOptions
import time
import pandas as pd
import datetime
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from webdriver_manager.chrome import ChromeDriverManager
import requests 
import json
import pprint
import codecs
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.select import Select


class HEADER():
    USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36}"
    API_HEADRS = {
        'Content-Type': 'application/json; charset=utf-8',
    }

LOG_FILE_PATH = "./log_{datetime}.log"
EXP_CSV_PATH="./exp_list_{search_keyword}_{datetime}.csv"
log_file_path=LOG_FILE_PATH.format(datetime=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S'))


### Chromeを起動する関数
def set_driver(driver_path, headless_flg):
    # Chromeドライバーの読み込み
    options = webdriver.ChromeOptions()

    # ヘッドレスモード（画面非表示モード）をの設定
    if headless_flg == True:
        options.add_argument('--headless')

    # 起動オプションの設定
    options.add_argument(
        '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36')
    # options.add_argument('log-level=3')
    options.add_argument('--ignore-certifica-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--incognito')          # シークレットモードの設定を付与

    # ChromeのWebDriverオブジェクトを作成する。
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

### ログファイルおよびコンソール出力
def log(txt):
    now=datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
    logStr = '[%s: %s] %s' % ('log',now , txt)
    # ログ出力
    with open(log_file_path, 'a', encoding='utf-8_sig') as f:
        f.write(logStr + '\n')
    print(logStr)

def find_table_target_word(th_elms, td_elms, target:str):
    # tableのthからtargetの文字列を探し一致する行のtdを返す
    for th_elm,td_elm in zip(th_elms,td_elms):
        if th_elm.text == target:
            return td_elm.text

def chs(user_id:str, search_keyword:str, driver:WebDriver):
    '''
    user_id:対象のインスタアカウントのID(urlの{user_id}の部分　https://www.instagram.com/{user_id}/)
    '''
    
    # ユーザー情報にアクセス
    driver.get(f"https://www.instagram.com/{user_id}/?__a=1")
    time.sleep(5)
    # データを取得
    res = json.loads(driver.find_element_by_tag_name('body').text)
    try:
        address = json.loads(res["graphql"]["user"]["business_address_json"])
        business_phone_number = res["graphql"]["user"]["business_phone_number"]
        street_address=address["street_address"]
        connected_fb_page = res["graphql"]["user"]["connected_fb_page"]
        print(res["graphql"]["user"]["full_name"], res["graphql"]["user"]["business_phone_number"], 
        address['zip_code'], address["street_address"], res["graphql"]["user"]["connected_fb_page"])
        return res["graphql"]["user"]["full_name"], res["graphql"]["user"]["business_phone_number"], address['zip_code'], address["street_address"], res["graphql"]["user"]["connected_fb_page"]
    except Exception as e:
        print(e)

@ eel.expose
### main処理
def main(search_keyword):
    log("処理開始")
    log("検索キーワード:{}".format(search_keyword))
    driver = set_driver("chromedriver.exe", False)
    url = "https://www.instagram.com/"
    url2 = "https://www.instagram.com/explore/tags/{}/".format(search_keyword)
    driver.get(url)
    time.sleep(3)
    driver.find_element_by_name("username").send_keys("kanjikw2330@gmail.com")
    driver.find_element_by_name("password").send_keys("1a2M3Y@0")
    # 検索ボタンクリック
    time.sleep(3)
    driver.find_element_by_css_selector('[type="submit"]').click()
    time.sleep(3)
    driver.get(url2)
    time.sleep(3)
    for i in range(5):
        driver.execute_script('window.scroll(0,100000000);')
        time.sleep(3)  
    posts_list = driver.find_elements_by_css_selector(".v1Nh3.kIKUG._bz0w a")
    time.sleep(3)
    p_list=[]
    df=pd.DataFrame()
    for post in posts_list:
        p = post.get_attribute("href")
        p_list.append(p)
        print(p)
    for p in p_list:
        driver.get(p)
        time.sleep(3)
        c = driver.find_element_by_css_selector(".sqdOP.yWX7d._8A5w5.ZIAjV").text
        b = driver.find_element_by_css_selector(".sqdOP.yWX7d._8A5w5.ZIAjV").click()
        time.sleep(3)
        a = driver.find_elements_by_class_name("_8FvLi")
        if len(a)>=1:
            print(c)
            (data_name,data_phone_number,data_zipcode,data_address,data_url)=chs(user_id=c, search_keyword=search_keyword,  driver=driver)
            now = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            df = df.append(
                {"店舗名": data_name,
                "電話番号": data_phone_number,
                "郵便番号": data_zipcode,
                "住所": data_address,
                "URL": data_url},
                ignore_index=True)
            df.to_csv(EXP_CSV_PATH.format(search_keyword=search_keyword,datetime=now), encoding="utf-8-sig")
            print("書き込み完了")
    time.sleep(1)
   
# 直接起動された場合はmain()を起動(モジュールとして呼び出された場合は起動しないようにするため)
if __name__ == "__main__":
   main()