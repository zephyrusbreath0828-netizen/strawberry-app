import streamlit as st
import google.generativeai as genai
from PIL import Image
import json

# --- APIキーの設定 ---
try:
    API_KEY = st.secrets["GOOGLE_API_KEY"]
    genai.configure(api_key=API_KEY)
except Exception as e:
    st.error("APIキーが設定されていません。StreamlitのSecrets設定を確認してください。")
    st.stop()

# モデルの指定
model = genai.GenerativeModel('gemini-1.5-flash')

# --- プロンプトの定義 ---
PROMPT = """
あなたはイチゴ栽培の専門家であり、高度な画像解析AIです。
ユーザーから提供されたイチゴの株の画像を解析し、以下の項目について詳細な評価とコメントを行ってください。
必ず以下のJSONフォーマットのみで出力してください。

{
  "overall_score": 85,
  "growth_analysis": {
    "vigor": "葉の茂り具合（草勢）の評価とコメント",
    "stage": "生育ステージの判定（例：栄養成長期、開花期など）",
    "flowers": "花の数と状態の評価",
    "fruits": "果実の熟度や状態の評価"
  },
  "health_analysis": {
    "leaf_color": "葉の色の異常（栄養障害など）の有無とコメント",
    "disease": "病気のサイン（うどんこ病、炭疽病など）の有無とコメント",
    "pest": "害虫の被害（食害、ハダニなど）の有無とコメント",
    "physical_stress": "物理的なストレス（チップバーン、乾燥など）の有無とコメント"
  },
  "comprehensive_advice": "総合的なアドバイスや次に取るべきアクション"
}
"""

# --- WebアプリのUI部分 ---
st.title("🍓 イチゴの総合健康診断アプリ")
st.write("イチゴの写真をアップロードすると、AIが成長と健康の全項目を詳細に分析します！")

uploaded_file = st.file_uploader("イチゴの画像を選択してください", type=["jpg", "jpeg", "png"])

if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="アップロードされた画像", use_column_width=True)

    if st.button("AIで総合診断する"):
        with st.spinner("AIが画像を詳細に解析中です..."):
            try:
                # Gemini APIに画像とプロンプトを送信
                response = model.generate_content(
                    [PROMPT, image],
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                )

                # 結果をJSONとして読み込む
                result = json.loads(response.text)

                # --- 結果の表示 ---
                st.header("📊 診断結果")
                
                # 総合スコア
                st.metric("総合健康スコア", f"{result.get('overall_score', 0)} / 100")

                # 成長度合いの表示
                st.subheader("🌱 成長度合いの評価")
                growth = result.get("growth_analysis", {})
                st.write(f"**生育ステージ:** {growth.get('stage', '不明')}")
                st.write(f"**葉の茂り具合 (草勢):** {growth.get('vigor', '不明')}")
                st.write(f"**花の状態:** {growth.get('flowers', '不明')}")
                st.write(f"**果実の状態:** {growth.get('fruits', '不明')}")

                st.divider()

                # 健康度合いの表示
                st.subheader("🩺 健康度合いの評価")
                health = result.get("health_analysis", {})
                st.write(f"**葉の色 (栄養状態):** {health.get('leaf_color', '不明')}")
                st.write(f"**病気のサイン:** {health.get('disease', '不明')}")
                st.write(f"**害虫の被害:** {health.get('pest', '不明')}")
                st.write(f"**物理的ストレス:** {health.get('physical_stress', '不明')}")

                st.divider()

                # 総合アドバイス
                st.subheader("💡 総合アドバイス")
                st.info(result.get("comprehensive_advice", "アドバイスはありません。"))

            except Exception as e:
                st.error(f"エラーが発生しました: {e}")
                if 'response' in locals():
                    st.write("AIの出力結果（デバッグ用）:")
                    st.code(response.text)
