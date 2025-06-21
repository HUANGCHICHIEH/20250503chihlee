import pandas as pd
import streamlit as st

st.title("我的第一個Streamlit App")

st.write("這是一個簡單的Streamlit應用程式。")

name = st.text_input("請輸入你的名字：")

if name:
    st.write(f"你好，{name}！")
