import streamlit as st
import google.generativeai as genai

st.title("🔍 使えるAIモデル調査ツール")

# APIキーの読み込み
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
    st.success("APIキーの読み込みに成功しました！")
except Exception as e:
    st.error("APIキーが設定されていません。")
    st.stop()

st.write("現在、あなたのAPIキーで利用可能なモデルの一覧を取得しています...")

try:
    # 利用可能なモデルの一覧を取得
    available_models = []
    for m in genai.list_models():
        # 画像解析（generateContent）に対応しているモデルだけを抽出
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
    
    if available_models:
        st.write("### ✅ 利用可能なモデル一覧")
        for model_name in available_models:
            st.code(model_name)
        
        st.info("上記の中に `models/gemini-1.5-flash` や `models/gemini-1.5-pro` などがあるか確認してください。")
    else:
        st.warning("画像解析に使えるモデルが見つかりませんでした。APIキーの権限などを確認してください。")

except Exception as e:
    st.error(f"モデル一覧の取得中にエラーが発生しました: {e}")
