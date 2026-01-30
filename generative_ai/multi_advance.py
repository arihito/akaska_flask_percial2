import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
config = genai.GenerationConfig(
    max_output_tokens=300,
    temperature=0.0,
)
def generate_content(model, prompt):
    response = model.generate_content(
        prompt, 
        generation_config=config
    )
    return response.text

import pandas as pd
data = {
    'レビュー文': [
        '感動的で、登場人物も魅力的だった',
        'ストーリーがあまり面白くなかった',
        '期待していたほど面白くなかった',
        '最高。この映画をずっと待っていた',
        '各シーンの映像が綺麗で、ロケ地に旅行したくなった',
    ]
}
df = pd.DataFrame(data)
# 複数のレビューを表に準備
def evaluate_review(review_text):
    few_shot_prompt = (
        f'''
        映画レビュー文を以下に分類してください。
        分類：
        - 高評価
        - 低評価
        
        テキスト：この映画はとても面白かったし、感動的だった。もう一度見たいと思った。
        評価：高評価
        テキスト：ストーリーが複雑で理解できなかったし、アクションシーンも退屈だった。
        評価：低評価
        テキスト：この映画はキャストもストーリーも素晴らしく、何度でも見たいと思える作品だった。
        評価：高評価
        テキスト：{review_text}\n
        評価：'''
    )
    response = generate_content(model, few_shot_prompt)
    if '高評価' in response:
        return '高評価'
    elif '低評価' in response:
        return '低評価'
    else:
        return '評価なし'
# applyは引数に関数名を渡すためレビュー文ごとに評価を追加
df['評価'] = df['レビュー文'].apply(evaluate_review)
print(df)
