import os
from dotenv import load_dotenv
import pandas as pd
import time
import matplotlib.pyplot as plt

import google.generativeai as genai

# 環境変数の読み込み
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# キーが見つからなかったらエラーを出力
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEYが環境変数に設定されていません")

# Geminiモデルの設定
genai.configure(api_key=GOOGLE_API_KEY)

model = genai.GenerativeModel('gemini-2.5-flash-lite')

# プロンプトをGeminiに渡し、戻ってきた解答をリターンする関数
def generate_content(prompt):
    config={
        "max_output_tokens": 2000, # 生成トークン数
        "temperature": 0 # 0.0:実直～1.0:曖昧
    }
    while True:
        try:
            # Geminiがプロンプト受けた何かしらのデータを返す
            response = model.generate_content(prompt, generation_config=config)
            return response.text
        except Exception as e:
            if "429" in str(e): # 使用枠の上限に達した場合のエラーコード
                print("1分間に使用できる上限に達しました。1分間待機します。")
                time.sleep(60)
            else:
                raise e # それ以外のエラー

# データフレームの内容からAIに総評分を作らせ、idと総評のリストにして返す関数
def create_summary(df):
    summary_list = []
    # groupは行だけを集めたデータフレーム
    for product_id, group in df.groupby('product_id'):
        comments = group['free_comment'].dropna().tolist() # リストに変換
        # コメントがあれば
        if comments:
            combined_text = "¥n".join(comments)
            # 以下の文末に挿入
            prompt = (
                f"""以下のレビューコメントを読んで、全体の総評（ポジティブ・ネガティブ・改善点などを含む短いまとめ）を作成してください。文の始まりは「総評：」にしてください。¥n¥n"""
                f"{combined_text}¥n¥n総評："
            )
            overall_summary = generate_content(prompt)
        else:
            overall_summary = "コメントなし"
        summary_list.append({ # 辞書形式にまとめる
            "product_id": product_id,
            "summary": overall_summary
        })
    return summary_list

# グラフ作成するための関数
def show_summary(df):
    # groupbyで平均を計算
    avg_scores = df.groupby("product_id")["score"].mean()
    # 棒グラフ作成
    fig, ax = plt.subplots(figsize=(6,4)) # 出力サイズ
    avg_scores.plot(kind="bar", ax=ax, color="gray", edgecolor="black") # 生成形式
    ax.set_title("Average Score (by Product)")
    ax.set_xlabel("product_id")
    ax.set_ylabel("average score")
    ax.set_ylim(0,5)
    plt.show()
    
# メイン処理
df = pd.read_csv("reviews.csv")
summary_list = create_summary(df)
for summary in summary_list :
    print(summary["product_id"],end=":")
    print(summary["summary"])
show_summary(df)