# 今後機能追加されないため2026以降はgoogle-genaiを推奨
import google.generativeai as genai

# APIをgeminiライブラリに設定
import os
from dotenv import load_dotenv
load_dotenv()

# APIキー設定
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)

# 使用可能なGeminiモデルの種類を確認表示
# print('使用可能なGeminiのモデル一覧')
# for model in genai.list_models():
#     if 'generateContent' in model.supported_generation_methods:
#         print(model.name)

# 使用可能なGeminiモデルの選択（今回は無料の2.5-flash-lite）
# リクエスト数10回/分：トークン数2500字/分：20回/日
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
# print(f'選択されたモデル: {model.model_name}')

# 生成の設定
config = genai.GenerationConfig(
    max_output_tokens=2048, # 生成トークン数
    temperature=0.8, # 0.0~1.0で高い方が返答が硬く実直
)

# 返答方法を定義
def generate_content(model, prompt):
    response = model.generate_content(
        prompt, 
        generation_config=config
    )
    return response.text

# ユーザ入力から結果を返す
user_input = input('質問を入力してください：')
response = generate_content(model, user_input)
print(f'Gemini: {response}')