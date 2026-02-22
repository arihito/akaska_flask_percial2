"""
Gemini AI による固定ページコンテンツ生成
"""
import json
import re
from flask import current_app


def generate_fixed_page(title: str, existing_keys: list) -> dict | None:
    """
    Gemini API でタイトルから固定ページコンテンツを生成する。

    Returns:
        {"key": str, "content": str, "summary": str} or None (エラー時)
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
            max_output_tokens=2048,
            temperature=0.7,
        )

        existing_keys_str = ', '.join(existing_keys) if existing_keys else 'なし'

        prompt = f"""あなたはFlask技術ブログの記事ライターです。
以下のタイトルで固定ページのコンテンツを生成してください。

【タイトル】
{title}

【生成するもの】
1. key: タイトルから作る英小文字スラッグ（アンダースコア可・既存キーと重複不可）
   - 既存キー一覧: {existing_keys_str}
   - 例: flask_crud, user_auth, api_design

2. content: 約1000文字の技術解説HTML（<h2>, <h3>, <p>, <ul>, <li>等のHTMLタグを使用）
   - Jinja2タグ（{{% %}}, {{{{ }}}}）は絶対に含めない
   - コードブロックは <pre><code>...</code></pre> で囲む
   - &amp;, &lt;, &gt; 等HTMLエンティティを適切に使う

3. summary: 約200文字の日本語要約文（ページの内容を端的に説明）

【出力形式】
必ず以下のJSONのみを出力してください（説明文は不要）:
{{"key": "スラッグ", "content": "HTML本文", "summary": "要約文"}}"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=config,
        )

        text = response.text.strip()
        # JSONブロック（コードフェンス含む）を抽出
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            data = json.loads(json_match.group())
            for field in ['key', 'content', 'summary']:
                if field not in data:
                    print(f"######## Gemini応答にキー '{field}' がありません ########")
                    return None
            # key をサニタイズ（英小文字・数字・アンダースコアのみ・最大50文字）
            data['key'] = re.sub(r'[^a-z0-9_]', '_', data['key'].lower())[:50].strip('_')
            return data
        else:
            print(f"######## Gemini応答のJSON解析失敗: {text[:200]} ########")
            return None

    except Exception as e:
        print(f"######## Gemini AI固定ページ生成失敗: {e} ########")
        return None
