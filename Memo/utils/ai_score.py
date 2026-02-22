"""
Gemini AI による記事品質スコアリング
"""
import json
import re
from flask import current_app


def analyze_memo_quality(title: str, content: str) -> dict | None:
    """
    Gemini APIで記事品質をスコアリングする。

    Returns:
        {"information": int, "writing": int, "readability": int} or None (エラー時)
    """
    api_key = current_app.config.get('GOOGLE_API_KEY', '')
    if not api_key:
        print("######## GOOGLE_API_KEY が未設定です ########")
        return None

    try:
        from google import genai
        from google.genai.types import GenerateContentConfig

        client = genai.Client(api_key=api_key)
        MODEL_NAME = "gemini-2.5-flash-lite"
        config = GenerateContentConfig(
            max_output_tokens=256,
            temperature=0.3,
        )

        prompt = f"""以下の技術ブログ記事を3つの観点で0〜100のスコアで評価してください。

【タイトル】
{title}

【本文】
{content[:3000]}

【評価基準】
- information (情報量): 技術的な情報の量・深さ・具体性
- writing (文章力): 論理構成・説明のわかりやすさ・文法の正確性
- readability (可読性): コードブロックの適切さ・段落構成・見出しの使い方

【出力形式】
必ず以下のJSON形式のみを出力してください。説明文は不要です。
{{"information": 数値, "writing": 数値, "readability": 数値}}"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        text = response.text.strip()
        json_match = re.search(r'\{[^}]+\}', text)
        if json_match:
            scores = json.loads(json_match.group())
            for key in ['information', 'writing', 'readability']:
                if key not in scores:
                    print(f"######## Gemini応答にキー '{key}' がありません: {text} ########")
                    return None
                scores[key] = max(0, min(100, int(scores[key])))
            return scores
        else:
            print(f"######## Gemini応答のJSON解析失敗: {text} ########")
            return None

    except Exception as e:
        print(f"######## Gemini API呼び出し失敗: {e} ########")
        return None
