from google import genai
from google.genai.types import GenerateContentConfig
import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
client = genai.Client(api_key=GOOGLE_API_KEY)
MODEL_NAME = "gemini-2.5-flash-lite"
config = GenerateContentConfig(
    max_output_tokens=2048,  # トークン制限
    temperature=0.0, # ランダム出力制限し再現性重視
)
def generate_content(prompt: str) -> str:
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=config,
    )
    return response.text
review_text = '最高だったのは予告編までだった'
# フューショットラーニングで幾つかの例で学習向上
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
    レビュー：{review_text}\n
    評価：'''
)
print(generate_content(few_shot_prompt))
