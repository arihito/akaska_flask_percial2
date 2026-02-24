"""
Gemini 2.0 Flash (image generation) によるユーザーサムネイル画像生成
モデル: gemini-2.0-flash-exp-image-generation（無料枠・同じ GOOGLE_API_KEY を使用）
"""
import io
from flask import current_app


def _apply_circular_mask(image_bytes: bytes) -> bytes:
    """
    生成画像に円形マスクを適用し、円の外側を透過にした PNG を返す。
    Gemini は透過 PNG を直接生成できないため後処理で対応。
    """
    from PIL import Image, ImageDraw

    img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")

    # 正方形にクロップ
    size = min(img.size)
    left = (img.width  - size) // 2
    top  = (img.height - size) // 2
    img  = img.crop((left, top, left + size, top + size))

    # 512x512 にリサイズ（他サムネイルと揃える）
    img = img.resize((512, 512), Image.LANCZOS)

    # 円形マスク作成（円内：不透明 / 円外：透明）
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse((0, 0, img.size[0] - 1, img.size[1] - 1), fill=255)
    img.putalpha(mask)

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def generate_thumb_image() -> bytes | None:
    """
    Gemini 2.0 Flash でフラットイラスト風アバターアイコン画像を生成する。
    生成後に円形マスクで背景を透過にして返す。

    Returns:
        PNG bytes (透過) or None（エラー時）
    """
    api_key = current_app.config.get('GOOGLE_API_KEY', '')
    if not api_key:
        print("######## GOOGLE_API_KEY が未設定です ########")
        return None

    try:
        from google import genai
        from google.genai.types import GenerateContentConfig

        client = genai.Client(api_key=api_key)
        MODEL_NAME = "gemini-2.0-flash-exp-image-generation"

        prompt = (
            "Flat vector illustration profile icon. "
            "A young IT student developer with glasses sitting at a laptop computer and coding. "
            "Circular composition with a vibrant solid colored background circle. "
            "Flat design style, clean and minimal. "
            "Similar to app avatar icons from Flaticon. "
            "No text, no shadows, no gradients. "
            "Square canvas, icon suitable for a profile picture."
        )

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=GenerateContentConfig(
                response_modalities=["IMAGE", "TEXT"],
            ),
        )

        for part in response.candidates[0].content.parts:
            if part.inline_data is not None:
                raw_bytes = part.inline_data.data
                return _apply_circular_mask(raw_bytes)

        print("######## Gemini 画像生成: レスポンスに画像データなし ########")
        return None

    except Exception as e:
        print(f"######## Gemini 画像生成失敗: {e} ########")
        return None
