"""
Gemini AI による翻訳価値スコアリング（グローバルSEO観点）
CLAUDE.translate.md の評価モデルに基づく100点満点スコアリング
"""
import json
import re
from flask import current_app


def score_translate_value(
    title: str,
    content: str,
    like_count: int = 0,
    view_count: int = 0,
) -> dict | None:
    """
    Gemini API で記事の翻訳価値をスコアリングする。

    Returns:
        {
            "seo": int,               # SEO検索ポテンシャル (0-40)
            "tech": int,              # 技術普遍性 (0-25)
            "structure": int,         # コンテンツ構造品質 (0-20)
            "spread": int,            # 拡散適性 (0-15)
            "translate_score": int,   # 総合スコア (0-100) ← Python側で合算
            "translate_verdict": str, # 判定文言
            "seo_title": str,         # 推奨英語SEOタイトル
            "keywords": list[str],    # 想定英語キーワード
            "inflow": str,            # 流入期待度（高/中/低）
            "translate_reason": str,  # 判定理由（80文字以内）
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
            max_output_tokens=512,
            temperature=0.3,
        )

        prompt = f"""あなたは「グローバルSEO戦略アナリスト兼テックコンテンツ評価AI」です。

以下の技術ブログ記事を、英語翻訳すべきかどうかの観点でスコアリングしてください。

【タイトル】
{title}

【本文】
{content[:3000]}

【エンゲージメント情報】
- いいね数: {like_count}
- 閲覧数: {view_count}

【評価基準】
① SEO検索ポテンシャル（最大40点）
- グローバル検索需要・エラー名含有・問題解決型（15点）
- キーワード明確性・英語SEOタイトル最適化可能性（10点）
- 検索意図一致度・実装手順型/エラー解決型（15点）

② 技術普遍性（最大25点）
- 国依存性の低さ（10点）
- 長期有効性・コア技術（10点）
- 応用可能性（5点）

③ コンテンツ構造品質（最大20点）
- コード具体性・実行可能コード例（10点）
- 論理構造・なぜそうなるか説明（10点）

④ 拡散適性（最大15点）
- SNS共有適性・タイトル即効性（5点）
- コミュニティ需要・StackOverflow的テーマ（5点）
- 既存エンゲージメント補正（いいね数・閲覧数）（5点）

【重要ルール】
- 文章の上手さより「集客資産価値」を重視
- 技術的普遍性を高く評価
- 問題解決型記事を優遇
- エラー記事は検索流入が強いため加点
- 単純な直訳ではなくSEO最適化翻訳前提で評価

【出力形式】
必ず以下のJSON形式のみを出力してください。説明文は不要です。
{{
    "seo": SEO評価の整数値(0-40),
    "tech": 技術普遍性の整数値(0-25),
    "structure": 構造品質の整数値(0-20),
    "spread": 拡散適性の整数値(0-15),
    "seo_title": "推奨英語SEOタイトル",
    "keywords": ["キーワード1", "キーワード2", "キーワード3"],
    "inflow": "高または中または低",
    "translate_reason": "判定理由（80文字以内）"
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
            print(f"######## Gemini翻訳スコア: JSON解析失敗: {text[:200]} ########")
            return None

        scores = json.loads(json_match.group())

        # スコア範囲バリデーション（Python側で合算・クランプ）
        seo       = max(0, min(40, int(scores.get('seo', 0))))
        tech      = max(0, min(25, int(scores.get('tech', 0))))
        structure = max(0, min(20, int(scores.get('structure', 0))))
        spread    = max(0, min(15, int(scores.get('spread', 0))))
        total     = seo + tech + structure + spread

        # 判定文言
        if total >= 80:
            verdict = "即翻訳推奨"
        elif total >= 75:
            verdict = "翻訳候補"
        elif total >= 60:
            verdict = "改善後再評価"
        else:
            verdict = "翻訳不要"

        return {
            "seo": seo,
            "tech": tech,
            "structure": structure,
            "spread": spread,
            "translate_score": total,
            "translate_verdict": verdict,
            "seo_title": str(scores.get('seo_title', '')),
            "keywords": scores.get('keywords', []),
            "inflow": str(scores.get('inflow', '低')),
            "translate_reason": str(scores.get('translate_reason', ''))[:80],
        }

    except Exception as e:
        print(f"######## Gemini翻訳スコア API呼び出し失敗: {e} ########")
        return None
