"""
Gemini AI による記事英語翻訳（SEO最適化翻訳）
"""
import json
import re
from flask import current_app


def translate_memo_to_english(title: str, content: str) -> dict | None:
    """
    Gemini API で記事タイトル・本文を SEO 最適化英語翻訳する。

    Returns:
        {
            "translated_title": str,
            "translated_body": str,
        }
        or None（エラー時）
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
            max_output_tokens=4096,
            temperature=0.3,
        )

        prompt = f"""あなたは「テック系コンテンツのSEO最適化英語翻訳者」です。

以下の日本語技術ブログ記事を英語に翻訳してください。

【翻訳方針】
- 単純な直訳ではなく、英語圏エンジニアが検索するキーワードを意識したSEO最適化翻訳を行う
- コードブロックはそのまま保持（コメントは英語化）
- Markdown形式を維持する
- タイトルはGoogle検索に最適化した英語タイトルにする
- 自然な英語表現を優先し、ぎこちない直訳を避ける

【タイトル】
{title}

【本文】
{content}

【出力形式】
必ず以下のJSON形式のみを出力してください。説明文は不要です。
{{
    "translated_title": "英語SEOタイトル",
    "translated_body": "英語Markdown本文（改行は\\nでエスケープ）"
}}"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        text = response.text.strip()
        # 改行ありJSONに対応
        json_match = re.search(r'\{[\s\S]+\}', text)
        if not json_match:
            print(f"######## Gemini翻訳: JSON解析失敗: {text[:200]} ########")
            return None

        result = json.loads(json_match.group())
        translated_title = str(result.get('translated_title', '')).strip()
        translated_body  = str(result.get('translated_body', '')).strip()

        if not translated_title or not translated_body:
            print(f"######## Gemini翻訳: 翻訳結果が空です ########")
            return None

        return {
            "translated_title": translated_title,
            "translated_body": translated_body,
        }

    except Exception as e:
        print(f"######## Gemini翻訳 API呼び出し失敗: {e} ########")
        return None
