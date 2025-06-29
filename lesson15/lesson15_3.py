import yfinance as yf
import os
import pandas as pd
import glob

# --- 1. Configuration Constants ---
DATA_DIR = 'data'
STOCK_MAPPING = {
    '2330': '台積電',
    '2303': '聯電',
    '2454': '聯發科',
    '2317': '鴻海'
}
TICKERS = [f"{code}.TW" for code in STOCK_MAPPING.keys()]


def download_data():
    """
    1. 下載yfinance的4檔股票資料。
    2. 在目前目錄下建立一個'data'資料夾。
    3. 下載的4檔股票必需儲存為4個csv檔，檔名包含股票中文名稱和當天日期 (e.g., 台積電_2024-06-02.csv)。
    4. 如果當天的檔案已存在，則不重複下載。
    5. 每次執行時會刪除該股票的舊日期檔案，只保留最新的一份。
    6. 採用一次性下載所有股票的方式以提升效率。
    """
    # 檢查並建立data資料夾
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    # 獲取今天的日期字串
    today_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    # 提升效率：一次性下載所有股票資料
    try:
        print("開始一次性下載所有股票數據...")
        all_data = yf.download(TICKERS, start='2000-01-01', end=today_date, auto_adjust=True)
        if all_data.empty:
            print("無法下載任何數據，程序終止。")
            return
        print("數據下載完成。")
    except Exception as e:
        print(f"下載數據時發生錯誤: {e}")
        return

    # 遍歷所有股票代碼，處理並儲存資料
    for ticker in TICKERS:
        base_code = ticker.split('.')[0]
        stock_name = STOCK_MAPPING[base_code]
        filename_today = f"{stock_name}_{today_date}.csv"
        filepath_today = os.path.join(DATA_DIR, filename_today)

        # 4. 如果當天的檔案已存在，則跳過
        if os.path.exists(filepath_today):
            print(f"今日檔案 '{filename_today}' 已存在，跳過處理。")
            continue

        # 5. 刪除舊日期的檔案
        old_files = glob.glob(os.path.join(DATA_DIR, f"{stock_name}_*.csv"))
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

def create_close_dataframe():
    """
    讀取 data 資料夾中最新的股票 CSV 檔，
    抽取 'Close' 欄位，並組合成一個 DataFrame。
    """
    all_close_series = {}

    for code, name in STOCK_MAPPING.items():
        # 尋找最新的 CSV 檔案
        search_pattern = os.path.join(DATA_DIR, f"{name}_*.csv")
        list_of_files = glob.glob(search_pattern)
        if not list_of_files:
            print(f"找不到 '{name}' ({code}) 的 CSV 檔案，跳過。")
            continue
        
        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"讀取檔案: {os.path.basename(latest_file)}")

        # 讀取並抽取資料 (只用 Date 和 Close)
        df = pd.read_csv(latest_file, index_col='Date', parse_dates=True, usecols=['Date', 'Close'])
        
        # 將 'Close' Series 加入字典，以中文名稱為 key
        all_close_series[name] = df['Close']

    if not all_close_series:
        print("沒有讀取到任何資料，無法建立 DataFrame。")
        return None

    # 組合成 DataFrame
    combined_df = pd.DataFrame(all_close_series)
    combined_df.sort_index(inplace=True)
    return combined_df

if __name__ == '__main__':
    download_data()
    close_df = create_close_dataframe()
    if close_df is not None:
        print("\n組合後的收盤價 DataFrame (最新五筆):")
        print(close_df.tail(5))