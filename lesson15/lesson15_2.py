import yfinance as yf
def download_data():
    import os
    import pandas as pd
    """
1.下載yfinance的4檔股票資料,股票有:2330.TW,2303.TW,2454.TW,2317.TW
2.在目前目錄下建立一個data的資料夾,如果已經有這個資料夾,就不建立
3.下載的4檔股票必需儲存為4個csv檔,檔名為2330.csv,2303.csv,2454.csv,2317.csv
4.如果已經有這些檔案,就不下載
"""    
    # 定義股票代碼列表
    tickers = ['2330.TW', '2303.TW', '2454.TW', '2317.TW']
    # 檢查並建立data資料夾
    data_dir = 'data'
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    # 遍歷所有股票代碼
    for ticker in tickers:
        base_code = ticker.split('.')[0]
        filename = f"{base_code}.csv"
        filepath = os.path.join(data_dir, filename)
        # 如果檔案已存在，則跳過下載
        if os.path.exists(filepath):
            print(f"{filename} 已存在，跳過下載。")
            continue
        try:
            print(f"下載股票數據： {ticker}...")
            # 獲取今天的日期字串，格式為 YYYY-MM-DD
            today_date = pd.Timestamp.today().strftime('%Y-%m-%d')
            data = yf.download(ticker, start='2000-01-01', end=today_date, auto_adjust=True, progress=False)
            if data.empty:
                print(f"找不到 {ticker} 的數據，跳過。")
                continue
            data.to_csv(filepath)
            print(f"儲存 {ticker} 至 {filepath}")
        except Exception as e:
            print(f"下載 {ticker} 時發生錯誤: {e}")
            
    
        
tw2330 = yf.download('2330.TW',start='2024-01-01',end='2024-06-01', auto_adjust=True)
tw2303 = yf.download('2303.TW',start='2024-01-01',end='2024-06-01', auto_adjust=True)
tw2454 = yf.download('2454.TW',start='2024-01-01',end='2024-06-01', auto_adjust=True)
tw2317 = yf.download('2317.TW',start='2024-01-01',end='2024-06-01', auto_adjust=True)

def main():
    download_data()
if __name__ == '__main__':
    main()