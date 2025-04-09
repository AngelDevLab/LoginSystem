import requests
import pandas as pd
import re
import sqlite3
import time
import math
import logging

from datetime import datetime, timedelta
from io import StringIO
from concurrent.futures import ThreadPoolExecutor
from tqdm import tqdm

from lib import database as my_db

REQUEST_DATA_ATTEMPT = 5

DATABASE = "stock.db"
DB_TABLE_INFO = "stock_info"
DB_TABLE_YEAR = lambda year: f"history_data_{year}"

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class StockInfo:
    @classmethod
    def _extract_number(cls, text):
        # 使用正規表達視察找數字部分
        match = re.search(r"(\d+(\.\d+)?)", text)
        if match:
            return float(match.group(1))  # 提取數字轉為浮點數
        else:
            return None  # 沒有數字返回 None

    @classmethod
    def _convert_to_iso_date(cls, date_str):
        # 將民國年轉為西元年
        date_str = date_str.replace("民國", "")
        year, month, day = map(int, date_str.split("/"))
        year += 1911
        iso_date = datetime(year, month, day).strftime("%Y-%m-%d")  # 轉換為 ISO日期格式
        return iso_date

    @classmethod
    def request(cls, market):
        """
        參考以下網址 https://mops.twse.com.tw/mops/web/t51sb01
        抓取上市櫃的股票資訊
        
        Parameters:
            market (str): 市場別,上市/上櫃    

        Returns:
            stock_info_dict (dict): 回傳以股票代號為鍵 StockBasicInfo 類為值得字典
                                    若字典為空表示 request 失敗
        """

        stock_info_dict = {}
        market_param_dict = {"上市": "sii", "上櫃": "otc"}
        url = "https://mops.twse.com.tw/mops/web/ajax_t51sb01"

        data = {
            "encodeURIComponent": "1",
            "step": "1",
            "firstin": "1",
            "TYPEK": market_param_dict[market],
            "co_id": ""
        }

        try:
            res = requests.post(url, data=data)
            res.raise_for_status() #如果請求不成功,將引發異常

            html_content = StringIO(res.text)
            df = pd.read_html(html_content)[0]
            df.set_index("公司 代號", inplace=True)
            df = df[df.index.str.isnumeric()]
            
            for code, row in df.iterrows():
                capital_amount = int(str(row["實收資本額(元)"]).replace(",", ""))
                par_value = cls._extract_number(row["普通股每股面額"])
                listing_date = cls._convert_to_iso_date(str(row["上市日期"])) if market == "上市" else cls._convert_to_iso_date(str(row["上櫃日期"]))

                if par_value is not None:
                    issue_shares = int((capital_amount / par_value) / 1000) if par_value != 0 else None
                else:
                    issue_shares = None

                stock_info = {
                    "name": str(row["公司簡稱"]),
                    "market": str(market),
                    "industry": str(row["產業類別"]),
                    "listing_date": listing_date,
                    "capital_amount": capital_amount,
                    "par_value": par_value,
                    "issue_shares": issue_shares
                }

                stock_info_dict[str(code)] = stock_info

        except Exception as e:
            print(f">> [ERROR] {e}")

        return stock_info_dict

    @classmethod
    def update_to_db(cls, stock_info_dict):
        db = my_db.connection()
        cursor = db.cursor()

        # 創建表格（如果不存在）
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {DB_TABLE_INFO} (
                            code VARCHAR(10) PRIMARY KEY,
                            name VARCHAR(255),
                            market VARCHAR(50),
                            industry VARCHAR(100),
                            listing_date DATE,
                            capital_amount BIGINT,
                            par_value DECIMAL(10, 2),
                            issue_shares BIGINT)''')

        try:
            for code, info in stock_info_dict.items():
                # 使用 INSERT ... ON DUPLICATE KEY UPDATE 來插入或更新數據
                cursor.execute(f'''INSERT INTO {DB_TABLE_INFO} 
                                    (code, name, market, industry, listing_date, capital_amount, par_value, issue_shares)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE
                                    name=VALUES(name), 
                                    market=VALUES(market), 
                                    industry=VALUES(industry), 
                                    listing_date=VALUES(listing_date), 
                                    capital_amount=VALUES(capital_amount), 
                                    par_value=VALUES(par_value), 
                                    issue_shares=VALUES(issue_shares)''',
                            (code, info['name'], info['market'], info['industry'], info['listing_date'],
                                info['capital_amount'], info['par_value'], info['issue_shares']))

            # 提交交易
            db.commit()
        
        except Exception as e:
            db.rollback()
            raise e
        
        finally:
            cursor.close()
            db.close()

    @staticmethod
    def read():
        # 使用 my_db.connection() 來取得 MySQL 資料庫連接
        db = my_db.connection()
        cursor = db.cursor()

        try:
            # 從資料表中讀取所有數據
            cursor.execute(f"SELECT * FROM {DB_TABLE_INFO}")
            rows = cursor.fetchall()

            stock_info_dict = {}
            for row in rows:
                # 將資料表中的字段逐一解包
                code, name, market, industry, listing_date, capital_amount, par_value, issue_shares = row
                stock_info = {
                    "name": name,
                    "market": market,
                    "industry": industry,
                    "listing_date": listing_date,
                    "capital_amount": capital_amount,
                    "par_value": par_value,
                    "issue_shares": issue_shares
                }
                # 以股票代號 code 作為字典的鍵
                stock_info_dict[code] = stock_info
            
            return stock_info_dict
        
        except Exception as e:
            # 使用 logging 記錄錯誤
            logging.error(f"Error reading stock info: {e}", exc_info=True)
            return None
        
        finally:
            # 關閉游標和資料庫連接
            cursor.close()
            db.close()

class StockHistoryData:
    @classmethod
    def _request_listed_stock_data(cls, stock_code, date):
        """
        Parameters:
            code (str): 股票代號
            date (str): 日期 格式為 "YYYYMM"

        Returns:
            data_list (list): 回傳股票列表
        """

        request_date = f"{date}01"
        url = f"https://www.twse.com.tw/exchangeReport/STOCK_DAY?response=json&date={request_date}&stockNo={stock_code}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        error_list = []
        for attempt in range(REQUEST_DATA_ATTEMPT):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                if response.status_code == 200:
                    data = response.json()

                    if data["stat"] != "OK":
                        error_list.append(f"data stat is not OK : {data['stat']}")
                        continue
                    if data["date"] != request_date:
                        error_list.append(f"data date not the same : {data['date']},{request_date}")
                        continue

                    stock_data = []
                    for row in data["data"]:
                        year, month, day = map(int, row[0].split('/'))
                        date_str = datetime(year + 1911, month, day).strftime('%Y-%m-%d')
                        volume = "{:,.0f}".format(float(row[1].replace(',', '')) / 1000) # 上市為股數不是張數，要轉換
                        stock_data.append((stock_code, date_str, volume) + tuple(row[2:]))
                    return stock_data
                else:
                    error_list.append(f"response status_code is not 200 : {response.status_code}")
                    continue
            except requests.HTTPError:
                error_list.append("requests HTTPError")
                continue
            finally:
                pass

        if len(error_list) == REQUEST_DATA_ATTEMPT:
            if all(elem == error_list[0] for elem in error_list):
                if error_list[0] != "data stat is not OK : 很抱歉，沒有符合條件的資料!":
                    logging.error(f">> [ERROR] {url}")
                    logging.error(error_list[0])
            else:
                for item in error_list:
                    error_filter_val = {"data stat is not OK : 很抱歉，沒有符合條件的資料!", 
                                        "data stat is not OK : 查詢日期小於99年1月4日，請重新查詢!",
                                        "data stat is not OK : 查詢日期大於今日，請重新查詢!"}
                    if not any(value in error_list for value in error_filter_val):
                        logging.error(f">> [ERROR] {url}")
                        logging.error(item)

        return None

    @classmethod
    def _request_otc_stock_data(cls, stock_code, date):
        """
        Parameters:
            code (str): 股票代號
            date (str): 日期 格式為 "YYYYMM"

        Returns:
            data_list (list): 回傳股票列表
        """

        request_date = f"{(int(date[:4]) - 1911):03d}/{date[4:]}"
        url = f"https://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_result.php?l=zh-tw&d={request_date}&stkno={stock_code}"

        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        error_list = []
        for attempt in range(REQUEST_DATA_ATTEMPT):
            try:
                response = requests.get(url, headers=headers)
                response.raise_for_status()
                
                if response.status_code == 200:
                    data = response.json()

                    if data["stkNo"] != stock_code:
                        error_list.append(f"data stkNo not the same : {data['stkNo']},{stock_code}")
                        continue
                    if data["reportDate"] != request_date:
                        error_list.append(f"data date not the same : {data['reportDate']},{request_date}")
                        continue
                    if data["iTotalRecords"] == 0:
                        error_list.append(f"data len is 0")
                        continue

                    stock_data = []
                    for row in data['aaData']:
                        year, month, day = map(int, row[0].replace('＊', '').split('/'))
                        date_str = datetime(year + 1911, month, day).strftime('%Y-%m-%d')
                        stock_data.append((stock_code, date_str,) + tuple(row[1:]))
                    return stock_data
                else:
                    error_list.append(f"response status_code is not 200 : {response.status_code}")
                    continue
            except requests.HTTPError:
                error_list.append("requests HTTPError")
                continue
            except Exception as e:
                error_list.append(f"other error : {e}")
                continue
            finally:
                pass

        if len(error_list) == REQUEST_DATA_ATTEMPT:
            if all(elem == error_list[0] for elem in error_list):
                if error_list[0] != "data len is 0":
                    logging.error(f">> [ERROR] {url}")
                    logging.error(error_list[0])
            else:
                for item in error_list:
                    error_filter_val = {"data stat is not OK : 很抱歉，沒有符合條件的資料!", 
                                        "data stat is not OK : 查詢日期小於99年1月4日，請重新查詢!",
                                        "data stat is not OK : 查詢日期大於今日，請重新查詢!"}
                    if not any(value in error_list for value in error_filter_val):
                        logging.error(f">> [ERROR] {url}")
                        logging.error(item)

        return None
    
    @classmethod
    def _update_stock_data_to_db(cls, form_name, stock_data_package_list):
        # 使用 MySQL 连接
        db = my_db.connection()
        cursor = db.cursor()

        # 创建表格（如果不存在）
        cursor.execute(f'''CREATE TABLE IF NOT EXISTS {form_name} (
                            code VARCHAR(10),
                            date DATE,
                            volume VARCHAR(20),
                            amount VARCHAR(20),
                            open VARCHAR(15),
                            high VARCHAR(15),
                            low VARCHAR(15),
                            close VARCHAR(15),
                            price_change VARCHAR(15),
                            transaction_count VARCHAR(20),
                            PRIMARY KEY (code, date)
                        )''')

        try:
            # 插入数据，使用 INSERT IGNORE 防止主键重复时插入失败
            cursor.executemany(f'''INSERT IGNORE INTO {form_name} 
                                    (code, date, volume, amount, open, high, low, close, price_change, transaction_count)
                                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)''', stock_data_package_list)

            # 提交事务
            db.commit()
        
        except Exception as e:
            # 出现异常时回滚事务
            db.rollback()
            raise e
        
        finally:
            # 关闭游标和数据库连接
            cursor.close()
            db.close()

    @classmethod
    def _update_data_to_db(cls, market, date):
        request_func = cls._request_listed_stock_data if market == "上市" else cls._request_otc_stock_data

        stock_info_dict = StockInfo.read()
        stock_codes = [code for code, info in stock_info_dict.items() if info['market'] == market]

        # 使用 ThreadPoolExecutor 來並行處理多個股票資料抓取任務
        with ThreadPoolExecutor(max_workers=5) as executor:
            # 使用 executor.map 方法並行處理多個股票代碼，並將結果收集起來
            stock_data_list = list(tqdm(executor.map(lambda code: request_func(code, date), stock_codes), total=len(stock_codes), desc=f"{market} {date}"))

        # 將所有股票資料合併成一個列表
        stock_data_package_list = [data for sublist in stock_data_list if sublist for data in sublist]

        year = date[:4]

        # 插入股票資料到資料庫
        cls._update_stock_data_to_db(DB_TABLE_YEAR(year), stock_data_package_list)

    @classmethod
    def update_month(cls, date):
        """
            date 格式為 "YYYYMM"
        """

        cls._update_data_to_db("上市", date)
        cls._update_data_to_db("上櫃", date)
