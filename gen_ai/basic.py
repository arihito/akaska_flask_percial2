# 2026以降も継続的に機能追加される公式 SDK
from google import genai
from google.genai.types import GenerateContentConfig
import os
from dotenv import load_dotenv
load_dotenv()

# APIキー設定
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]

# Client を明示的に生成
client = genai.Client(api_key=GOOGLE_API_KEY)

# 使用する Gemini モデル
# 無料枠: gemini-2.5-flash-lite
# リクエスト数10回/分：トークン数2500字/分：20回/日
MODEL_NAME = "gemini-2.5-flash-lite"

# 生成設定（旧 GenerationConfig 相当）
config = GenerateContentConfig(
    max_output_tokens=2048, # 生成トークン数
    temperature=0.8, # 0.0~1.0で高い方が返答が硬く実直
)

# 返答生成関数
def generate_content(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text

# ユーザ入力から結果を返す
user_input = input("質問を入力してください：")
response = generate_content(user_input)
print(f"Gemini: {response}")
