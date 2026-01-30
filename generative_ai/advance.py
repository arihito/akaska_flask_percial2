import google.generativeai as genai
import os
from dotenv import load_dotenv
load_dotenv()
GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('models/gemini-2.5-flash-lite')
config = genai.GenerationConfig(
    max_output_tokens=300, # トークン制限
    temperature=0.0, # ランダム出力制限し再現性重視
)
def generate_content(model, prompt):
    response = model.generate_content(
        prompt, 
        generation_config=config
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
print(generate_content(model, few_shot_prompt))