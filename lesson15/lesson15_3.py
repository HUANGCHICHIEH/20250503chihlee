import yfinance as yf
import os
import pandas as pd
import glob

def download_data():
    """
    1. 下載yfinance的4檔股票資料。
    2. 在目前目錄下建立一個'data'資料夾。
    3. 下載的4檔股票必需儲存為4個csv檔，檔名包含股票中文名稱和當天日期 (e.g., 台積電_2024-06-02.csv)。
    4. 如果當天的檔案已存在，則不重複下載。
    5. 每次執行時會刪除該股票的舊日期檔案，只保留最新的一份。
    6. 採用一次性下載所有股票的方式以提升效率。
    """
    # 定義股票代碼列表
    tickers = ['2330.TW', '2303.TW', '2454.TW', '2317.TW']
    # 定義股票代號與中文名稱的對應關係
    stock_mapping = {
        '2330': '台積電',
        '2303': '聯電',
        '2454': '聯發科',
        '2317': '鴻海'
    }

    # 檢查並建立data資料夾
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    # 獲取今天的日期字串
    today_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    # 提升效率：一次性下載所有股票資料
    try:
        print("開始一次性下載所有股票數據...")
        all_data = yf.download(tickers, start='2000-01-01', end=today_date, auto_adjust=True)
        if all_data.empty:
            print("無法下載任何數據，程序終止。")
            return
        print("數據下載完成。")
    except Exception as e:
        print(f"下載數據時發生錯誤: {e}")
        return

    # 遍歷所有股票代碼，處理並儲存資料
    for ticker in tickers:
        base_code = ticker.split('.')[0]
        stock_name = stock_mapping[base_code]
        filename_today = f"{stock_name}_{today_date}.csv"
        filepath_today = os.path.join(data_dir, filename_today)

        # 4. 如果當天的檔案已存在，則跳過
        if os.path.exists(filepath_today):
            print(f"今日檔案 '{filename_today}' 已存在，跳過處理。")
            continue

        # 5. 刪除舊日期的檔案
        old_files = glob.glob(os.path.join(data_dir, f"{stock_name}_*.csv"))
        for old_file in old_files:
            try:
                os.remove(old_file)
                print(f"已刪除舊檔案: {old_file}")
            except OSError as e:
                print(f"刪除檔案 {old_file} 時發生錯誤: {e}")

        # 從下載好的 all_data 中提取單一股票的資料並儲存
        try:
            stock_data = all_data.loc[:, (slice(None), ticker)]
            stock_data.columns = stock_data.columns.droplevel(1)
            stock_data.to_csv(filepath_today, encoding='utf-8-sig')
            print(f"儲存 {ticker} ({stock_name}) 至 {filepath_today}")
        except Exception as e:
            print(f"處理或儲存 {ticker} 時發生錯誤: {e}")

if __name__ == '__main__':
    download_data()