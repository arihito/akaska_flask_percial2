# コーディング規約（CODING STANDARDS）

このアプリケーションの既存コードから読み取れる命名規則・コーディングスタイル。

---

## 1. Python 命名規則

| 対象 | スタイル | 例 |
|------|---------|-----|
| 変数・関数 | snake_case | `user_id`, `created_at`, `save_upload()` |
| クラス（モデル・フォーム） | PascalCase | `User`, `Memo`, `MemoForm` |
| 定数・設定値 | UPPER_SNAKE_CASE | `STATIC_PAGES`, `UPLOAD_FOLDERS`, `ALLOWED_EXTENSIONS` |
| Blueprint変数 | `{name}_bp` | `auth_bp`, `memo_bp`, `public_bp` |
| テーブル名 | 英語複数形 | `users`, `memos`, `categories`, `favorites` |
| 中間テーブル | `{model1}_{model2}` 複数形 | `memo_categories` |

### クエリ変数の命名

```python
# JOIN等の生データは raw_ 接頭辞
raw_memos = db.session.query(Memo, func.count(...)).all()

# テンプレートに渡す整形済みデータは接頭辞なし
memos = [{"memo": m, "like_count": c} for m, c in raw_memos]
```

---

## 2. ファイル・ディレクトリ命名

| 対象 | パターン | 例 |
|------|---------|-----|
| Pythonファイル | snake_case.py | `user_factory.py`, `upload.py` |
| テンプレート | snake_case.j2（`.j2`拡張子で統一） | `login.j2`, `index.j2` |
| パーシャル | `_`接頭辞 + snake_case.j2 | `_formhelpers.j2`, `_categories.j2` |
| 画像（連番） | `{NN}.{ext}` | `01.jpg`, `02.png` |
| サンプルデータ | `{category}_{NNN}.md` | `basic_001.md`, `crud_002.md` |
| Factory | `{model_name}_factory.py` | `user_factory.py`, `body_factory.py` |

### Blueprint ディレクトリ構造

```
{blueprint_name}/
├── __init__.py     ← 空（パッケージマーカー）
└── views.py        ← Blueprint定義とルート関数
```

対応するテンプレートは `templates/{blueprint_name}/` に配置。

---

## 3. import 順序

```python
# 1. 標準ライブラリ
import os
import re
import math
from datetime import datetime, timedelta

# 2. サードパーティ
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from sqlalchemy import func, asc, desc, or_

# 3. ローカル（プロジェクト内）
from models import db, User, Memo, Favorite, Category
from forms import MemoForm
from utils.upload import save_upload
```

---

## 4. コメント規約

### セクション区切り

```python
# ---- セクション名 ----
base_query = (...)

# ---- 総件数（ページ数算出用）----
total = base_query.count()
```

### 処理説明コメント

```python
# メールアドレスを空白削除小文字に変換して1件分のユーザー情報を取得
user = User.query.filter_by(email=form.email.data.strip().lower()).first()
```

- コメントは**日本語**で記述
- UI表示文字列（flash、バリデーションメッセージ等）も**日本語**
- 変数名・関数名・クラス名は**英語**

---

## 5. SQLAlchemy パターン

### クエリのメソッドチェーン

```python
raw_memos = (
    db.session.query(Memo, func.count(Favorite.id).label("like_count"))
    .outerjoin(Favorite, Memo.id == Favorite.memo_id)
    .filter(Memo.user_id == current_user.id)
    .group_by(Memo.id)
    .order_by(order_by_clause)
    .limit(per_page)
    .offset(offset)
    .all()
)
```

- 括弧で囲み、各メソッドを改行してインデント
- `.label("alias")` でSQLエイリアスを付与

### 条件の積み上げ

```python
base_query = db.session.query(Memo, ...)
if q:
    base_query = base_query.filter(
        or_(Memo.title.ilike(f"%{q}%"), Memo.content.ilike(f"%{q}%"))
    )
if category_id:
    base_query = base_query.filter(Memo.categories.any(Category.id == category_id))
```

### 取得パターン

```python
user = User.query.filter_by(email=email).first()     # 0件ならNone
memo = Memo.query.get_or_404(memo_id)                 # 0件なら404
categories = Category.query.order_by(Category.name).all()
```

---

## 6. テンプレート規約

### 5層継承構造

```
layout/head.j2          ← HTML基本構造・CDN読み込み
  └→ layout/mode.j2     ← ダークモード切り替え・フッター
      └→ base.j2        ← グローバルナビ・メインコンテナ
          └→ {bp}/base.j2  ← 分野別レイアウト（サイドメニュー等）
              └→ page.j2   ← 各ページ（index, create等）
```

### ブロック名

| ブロック名 | 用途 |
|-----------|------|
| `body` | HTML `<body>` 全体 |
| `container` | メインコンテナ領域 |
| `content` | ページコンテンツ本体 |
| `title` | ページタイトル・ヘッダー |

### パーシャルの使い方

```jinja2
{# マクロのインポート #}
{% from "auth/_formhelpers.j2" import render_floating_field %}

{# レイアウトパーツの埋め込み #}
{% include 'layout/globalnav.j2' %}
{% include 'layout/footer.j2' %}
```

### カスタムフィルター

```jinja2
{{ memo.content | markdown }}                     {# Markdown→HTML変換 #}
{{ memo.content | truncate(200, False, '...') }}  {# テキスト省略 #}
{{ memo.created_at.strftime("%Y年%m月%d日") }}      {# 日付フォーマット #}
```

---

## 7. JavaScript 規約

### モジュールパターン

```javascript
(() => {
    "use strict";
    // 処理
})();
```

### データ連携

```html
<!-- HTML側: data-* 属性で値を埋め込み -->
<span class="like-area" data-memo-id="{{ memo.id }}"></span>
```

```javascript
// JS側: dataset でキャメルケース変換して取得
const memoId = element.dataset.memoId;
```

### ローカルストレージ（テーマ管理）

```javascript
const getStoredTheme = () => localStorage.getItem("theme");
const setStoredTheme = (theme) => localStorage.setItem("theme", theme);
```

---

## 8. CSS 規約

### カスタムプロパティ（CSS変数）

```css
:root {
    --fs-base: 1rem;
    --fs-small: 0.85rem;
    --fs-md: 1.1rem;
    --fs-lg: 1.2rem;
    --fs-xl: 1.4rem;
}
```

### セクション区切り

```css
/* ============== 初期値 =============== */
/* ============== 共通部品 =============== */
/* ============== トップページ =============== */
/* ============== マイページ =============== */
/* ============== JS連携 =============== */
```

### クラス命名

- **Bootstrap標準**: `container`, `row`, `col`, `btn`, `form-control`, `card`, `badge`
- **独自クラス**: `fade-in`, `fade-delay-{N}`, `memo-img-wrap`, `user-icon`, `category_tag`, `like-area`, `key_visual`, `change-mode`

---

## 9. 固定ページ追加手順

`STATIC_PAGES` 辞書による一元管理のため、固定ページ追加は以下の3点セット：

1. `fixed/views.py` の `STATIC_PAGES` にキーと日本語タイトルを追加
2. `templates/fixed/{key}.j2` テンプレートを作成（`fixed/base.j2` を継承）
3. `static/images/fixed/{key}.jpg` キービジュアル画像を配置
