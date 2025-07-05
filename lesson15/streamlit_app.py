import streamlit as st
import pandas as pd
import lesson15_2 as data_manager
import plotly.express as px

# --- 1. 頁面設定 (Page Configuration) ---
# st.set_page_config 必須是第一個被呼叫的 Streamlit 命令
st.set_page_config(
    page_title="台灣股價儀表板",
    page_icon="📈",
    layout="wide"
)

# --- 2. 資料載入與快取 (Data Loading & Caching) ---
@st.cache_data(ttl=3600) # 快取資料一小時
def load_data():
    """
    這個函式會執行資料下載與處理。
    Streamlit 的 @st.cache_data 會快取結果，避免每次互動都重新下載。
    """
    with st.spinner('正在下載最新股價資料...'):
        data_manager.download_data()
    df = data_manager.create_close_dataframe()
    if df is not None:
        # 確保索引是 DatetimeIndex
        df.index = pd.to_datetime(df.index)
    return df

# --- 3. 主應用程式介面 (Main App Interface) ---
st.title("📈 台灣股價儀表板")
st.write("這是一個互動式的儀表板，用來視覺化分析您所選擇的台灣股票。")

# 載入資料
all_close_df = load_data()

if all_close_df is None or all_close_df.empty:
    st.error("無法載入資料。請確認 'data' 資料夾存在且 lesson15_2.py 可正常執行。")
else:
    # --- 4. 側邊欄控制項 (Sidebar Controls) ---
    st.sidebar.header("控制面板")

    # 股票選擇
    stock_list = all_close_df.columns.tolist()
    selected_stocks = st.sidebar.multiselect(
        "選擇股票:",
        options=stock_list,
        default=stock_list[:2]  # 預設選取前兩檔股票
    )

    # 日期範圍選擇
    min_date = all_close_df.index.min()
    max_date = all_close_df.index.max()

    selected_date_range = st.sidebar.date_input(
        "選擇日期範圍:",
        value=(min_date, max_date), # 預設為全部範圍
        min_value=min_date,
        max_value=max_date,
        format="YYYY-MM-DD"
    )

    # 技術分析選項
    st.sidebar.subheader("技術分析")
    show_ma = st.sidebar.checkbox("顯示移動平均線 (MA)")
    if show_ma:
        ma_period = st.sidebar.slider("移動平均天數:", 5, 100, 20)

    # --- 5. 主面板顯示 (Main Panel Display) ---
    if not selected_stocks:
        st.warning("請在左方側邊欄選擇至少一檔股票以顯示圖表。")
    else:
        # 根據使用者選擇過濾資料
        start_date, end_date = selected_date_range
        filtered_df = all_close_df.loc[start_date:end_date, selected_stocks]

        # 準備繪圖用的 DataFrame
        plot_df = filtered_df.copy()
        
        # 如果勾選，則計算並加入移動平均線
        if show_ma:
            for stock in selected_stocks:
                plot_df[f'{stock}_{ma_period}日MA'] = plot_df[stock].rolling(window=ma_period).mean()
        
        # 使用 Plotly 繪製更具互動性的圖表
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

        # 顯示資料表格
        st.subheader("股價資料預覽")
        st.dataframe(filtered_df.sort_index(ascending=False))

st.sidebar.success("介面設計完成！您可以開始互動操作。")