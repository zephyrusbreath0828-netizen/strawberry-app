import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- APIキーの設定 ---
# 実際の運用では環境変数やStreamlitのSecrets機能を使って隠してください
API_KEY = "AQ.Ab8RN6ISs9OLmZVqKRVrQL_tUpVfuxt8P3CvdQogN_nilCUPOw"
genai.configure(api_key=API_KEY)

# モデルの準備
model = genai.GenerativeModel('gemini-1.5-flash') # または gemini-1.5-pro

# --- プロンプトの定義 ---
PROMPT = """
あなたはイチゴ栽培の専門家であり、高度な画像解析AIです。
ユーザーから提供されたイチゴの株の画像を解析し、健康度合いや成長具合を数値化・評価してください。
以下のJSONフォーマットのみで出力してください。Markdownのコードブロックは使用しないでください。

{
  "health_score": 85,
  "growth_stage": "開花期 (Flowering)",
  "growth_score": 90,
  "issues_detected": ["葉の先端にわずかな枯れ"],
  "advice": "順調に成長しています。"
}
"""

# --- WebアプリのUI部分 (Streamlit) ---
st.title("🍓 イチゴ健康度チェックアプリ")
st.write("イチゴの写真をアップロードすると、AIが健康度や成長具合を判定します！")

# 画像アップロード機能
uploaded_file = st.file_uploader("イチゴの画像を選択してください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    # アップロードされた画像を表示
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)
    
    # 判定ボタン
    if st.button("AIで判定する"):
        with st.spinner("AIが画像を解析中です..."):
            try:
                # Gemini APIに画像とプロンプトを送信
                response = model.generate_content([PROMPT, image])
                
                # 結果をJSONとして読み込む
                result_json = json.loads(response.text)
                
                # 結果を画面に表示
                st.subheader("📊 判定結果")
                
                # メトリクス（数値）を並べて表示
                col1, col2 = st.columns(2)
                col1.metric("健康度 (Health Score)", f"{result_json['health_score']} / 100")
                col2.metric("成長具合 (Growth Score)", f"{result_json['growth_score']} / 100")
                
                st.write(f"**成長段階:** {result_json['growth_stage']}")
                
                st.write("**検出された異常:**")
                if result_json['issues_detected']:
                    for issue in result_json['issues_detected']:
                        st.write(f"- {issue}")
                else:
                    st.write("- なし（健康です！）")
                    
                st.info(f"**💡 アドバイス:**\n{result_json['advice']}")
                
            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.write("AIの出力が正しいJSON形式でなかった可能性があります。")
