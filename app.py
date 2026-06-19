import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- APIキーの設定 (Streamlit Cloud用) ---
# st.secretsを使って、安全にAPIキーを読み込みます
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("APIキーが設定されていません。StreamlitのSecrets設定を確認してください。")
    st.stop()

# モデルの準備
model = genai.GenerativeModel('gemini-1.5-flash')

# --- プロンプトの定義 ---
PROMPT = """
あなたはイチゴ栽培の専門家であり、高度な画像解析AIです。
ユーザーから提供されたイチゴの株の画像を解析し、健康度合いや成長具合を数値化・評価してください。
必ず以下のJSONフォーマットのみで出力してください。

{
  "health_score": 85,
  "growth_stage": "開花期 (Flowering)",
  "growth_score": 90,
  "issues_detected": ["葉の先端にわずかな枯れ"],
  "advice": "順調に成長しています。"
}
"""

# --- WebアプリのUI部分 ---
st.title("🍓 イチゴ健康度チェックアプリ")
st.write("イチゴの写真をアップロードすると、AIが健康度や成長具合を判定します！")

uploaded_file = st.file_uploader("イチゴの画像を選択してください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    if st.button("AIで判定する"):
        with st.spinner("AIが画像を解析中です..."):
            try:
                # Gemini APIに画像とプロンプトを送信（JSON形式を強制する設定を追加）
                response = model.generate_content(
                    [PROMPT, image],
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                )

                # 結果をJSONとして読み込む
                result_json = json.loads(response.text)

                # 結果を画面に表示
                st.subheader("📊 判定結果")

                col1, col2 = st.columns(2)
                col1.metric("健康度 (Health Score)", f"{result_json.get('health_score', 0)} / 100")
                col2.metric("成長具合 (Growth Score)", f"{result_json.get('growth_score', 0)} / 100")

                st.write(f"**成長段階:** {result_json.get('growth_stage', '不明')}")

                st.write("**検出された異常:**")
                issues = result_json.get('issues_detected', [])
                if issues:
                    for issue in issues:
                        st.write(f"- {issue}")
                else:
                    st.write("- なし（健康です！）")

                st.info(f"**💡 アドバイス:**\n{result_json.get('advice', 'アドバイスはありません。')}")

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                st.write("AIの出力結果:")
                st.code(response.text) # 原因調査のためにAIの実際の出力を表示します
