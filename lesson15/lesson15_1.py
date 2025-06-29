import pandas as pd
import yfinance as yf
import os
import glob
import streamlit as st
import plotly.express as px

# -- 1. Constants and Configuration --
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
    1. Downloads stock data for specified tickers.
    2. Creates a 'data' directory if it doesn't exist.
    3. Saves each stock as a CSV file named {code}_{date}.csv.
    4. Skips download if the file for today already exists.
    5. Deletes older files for each stock, keeping only the latest one.
    6. Uses a single batch download for efficiency.
    """
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    today_date = pd.Timestamp.today().strftime('%Y-%m-%d')

    # Check if all files for today already exist
    all_exist = all(os.path.exists(os.path.join(DATA_DIR, f"{STOCK_MAPPING[code]}_{today_date}.csv")) for code in STOCK_MAPPING.keys())
    if all_exist:
        print("All stock files for today already exist. Skipping download.")
        return

    # Efficiently download all data at once
    try:
        print("Downloading all stock data...")
        all_data = yf.download(TICKERS, start='2000-01-01', end=today_date, auto_adjust=True)
        if all_data.empty:
            print("No data downloaded. Aborting.")
            return
        print("Download complete.")
    except Exception as e:
        print(f"An error occurred during download: {e}")
        return

    # Process and save each stock's data
    for ticker in TICKERS:
        base_code = ticker.split('.')[0]
        stock_name = STOCK_MAPPING[base_code]
        filename_today = f"{stock_name}_{today_date}.csv"
        filepath_today = os.path.join(DATA_DIR, filename_today)

        # Clean up old files for this stock
        old_files = glob.glob(os.path.join(DATA_DIR, f"{stock_name}_*.csv"))
        for old_file in old_files:
            if old_file != filepath_today:
                try:
                    os.remove(old_file)
                    print(f"Removed old file: {old_file}")
                except OSError as e:
                    print(f"Error removing file {old_file}: {e}")

        # Extract and save the data for the current stock
        try:
            stock_data = all_data.loc[:, (slice(None), ticker)]
            stock_data.columns = stock_data.columns.droplevel(1) # Flatten MultiIndex
            if stock_data.empty:
                print(f"No data for {ticker}, skipping save.")
                continue
            stock_data.to_csv(filepath_today, encoding='utf-8-sig')
            print(f"Saved {ticker} ({stock_name}) to {filepath_today}")
        except KeyError:
            print(f"Could not find data for {ticker} in downloaded set.")
        except Exception as e:
            print(f"Error saving data for {ticker}: {e}")

def combine_close_prices():
    """
    Reads the latest CSV file for each stock from the 'data' directory,
    extracts the 'Close' column, and combines them into a single DataFrame.
    """
    all_close_series = {}

    for code, name in STOCK_MAPPING.items():
        # Find the latest CSV file for the stock
        search_pattern = os.path.join(DATA_DIR, f"{name}_*.csv")
        list_of_files = glob.glob(search_pattern)
        if not list_of_files:
            print(f"No CSV file found for {name} ({code}).")
            continue

        latest_file = max(list_of_files, key=os.path.getctime)
        print(f"Reading latest file for {name}: {os.path.basename(latest_file)}")

        # Read the 'Close' column, setting 'Date' as the index
        df = pd.read_csv(latest_file, index_col='Date', parse_dates=True, usecols=['Date', 'Close'])
        all_close_series[name] = df['Close']

    if not all_close_series:
        return pd.DataFrame()

    # Combine all Series into a single DataFrame
    combined_df = pd.DataFrame(all_close_series)
    combined_df.sort_index(inplace=True)
    return combined_df

# -- 2. Streamlit Application --
@st.cache_data(ttl=3600)  # Cache the data for 1 hour
def load_data():
    with st.spinner('正在下載最新股價資料...'):
        download_data()
    df = combine_close_prices()
    return df

def run_streamlit_app():
    st.set_page_config(page_title="股價儀表板", page_icon="📈", layout="wide")
    st.title("📈 台灣股價儀表板")
    st.write("這是一個互動式的儀表板，用來視覺化分析您所選擇的台灣股票。")

    df = load_data()

    if df.empty:
        st.error("無法載入資料，請檢查 'data' 資料夾或執行環境。")
        return

    # --- Sidebar Controls ---
    st.sidebar.header("控制面板")
    all_stocks = df.columns.tolist()
    selected_stocks = st.sidebar.multiselect(
        "選擇股票:", options=all_stocks, default=all_stocks[:2]
    )

    # 日期範圍選擇
    min_date = df.index.min()
    max_date = df.index.max()
    selected_date_range = st.sidebar.date_input(
        "選擇日期範圍:",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD"
    )

    # 技術分析選項
    st.sidebar.subheader("技術分析")
    show_ma = st.sidebar.checkbox("顯示移動平均線 (MA)")
    if show_ma:
        ma_period = st.sidebar.slider("移動平均天數:", 5, 100, 20)

    # --- Main Panel ---
    if not selected_stocks:
        st.warning("請從側邊欄選擇至少一檔股票。")
    else:
        # 根據使用者選擇過濾資料
        start_date, end_date = selected_date_range
        filtered_df = df.loc[start_date:end_date, selected_stocks]

        # 準備繪圖用的 DataFrame
        plot_df = filtered_df.copy()
        
        # 如果勾選，則計算並加入移動平均線
        if show_ma:
            for stock in selected_stocks:
                plot_df[f'{stock}_{ma_period}日MA'] = plot_df[stock].rolling(window=ma_period).mean()

        # Display interactive chart
        st.subheader("股價收盤價走勢圖")
        fig = px.line(plot_df, x=plot_df.index, y=plot_df.columns,
                      labels={'value': '股價 (TWD)', 'Date': '日期', 'variable': '圖例'})
        st.plotly_chart(fig, use_container_width=True)

        # 顯示最新股價與漲跌幅
        st.subheader("最新股價與單日漲跌")
        if len(filtered_df) > 1:
            latest_row = filtered_df.iloc[-1]
            previous_row = filtered_df.iloc[-2]
            
            cols = st.columns(len(selected_stocks))
            for i, stock in enumerate(selected_stocks):
                with cols[i]:
                    latest_price = latest_row[stock]
                    price_change = latest_price - previous_row[stock]
                    percent_change = (price_change / previous_row[stock]) * 100
                    st.metric(
                        label=stock, 
                        value=f"{latest_price:,.2f} TWD",
                        delta=f"{price_change:,.2f} ({percent_change:.2f}%)"
                    )
        else:
            st.info("需要至少兩天資料才能計算漲跌幅。")

        # Display data table
        st.subheader("股價資料預覽")
        st.dataframe(filtered_df.sort_index(ascending=False))

    st.sidebar.success("介面設計完成！您可以開始互動操作。")

if __name__ == '__main__':
    run_streamlit_app()