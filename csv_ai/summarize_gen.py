import os
from dotenv import load_dotenv
import pandas as pd
import time
import matplotlib.pyplot as plt

from google import genai
from google.genai import types

# 環境変数の読み込み
load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

# キーが見つからなかったらエラーを出力
if not GOOGLE_API_KEY:
    raise ValueError("GOOGLE_API_KEYが環境変数に設定されていません")

# GenAI クライアント作成（新方式）
client = genai.Client(api_key=GOOGLE_API_KEY)

MODEL_NAME = "gemini-2.5-flash-lite"

# プロンプトをGeminiに渡して結果を返す関数
def generate_content(prompt: str) -> str:
    config = types.GenerateContentConfig(
        max_output_tokens=2000,
        temperature=0.0,
    )

    while True:
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config,
            )
            return response.text

        except Exception as e:
            if "429" in str(e):
                print("1分間に使用できる上限に達しました。1分間待機します。")
                time.sleep(60)
            else:
                raise


# データフレームの内容から総評を生成
def create_summary(df: pd.DataFrame):
    summary_list = []

    for product_id, group in df.groupby("product_id"):
        comments = group["free_comment"].dropna().tolist()

        if comments:
            combined_text = "\n".join(comments)
            prompt = (
                "以下のレビューコメントを読んで、全体の総評"
                "（ポジティブ・ネガティブ・改善点などを含む短いまとめ）を作成してください。\n"
                "文の始まりは「総評：」にしてください。\n\n"
                f"{combined_text}\n\n総評："
            )
            overall_summary = generate_content(prompt)
        else:
            overall_summary = "コメントなし"

        summary_list.append({
            "product_id": product_id,
            "summary": overall_summary,
        })

    return summary_list


# グラフ表示
def show_summary(df: pd.DataFrame):
    avg_scores = df.groupby("product_id")["score"].mean()

    fig, ax = plt.subplots(figsize=(6, 4))
    avg_scores.plot(kind="bar", ax=ax, color="gray", edgecolor="black")
    ax.set_title("Average Score (by Product)")
    ax.set_xlabel("product_id")
    ax.set_ylabel("average score")
    ax.set_ylim(0, 5)
    plt.show()


# メイン処理
df = pd.read_csv("reviews.csv")

summary_list = create_summary(df)
for summary in summary_list:
    print(f"{summary['product_id']}:{summary['summary']}")

show_summary(df)
