# 用語集（GLOSSARY）

このアプリケーションで使用されるドメイン用語の定義。

---

## モデル（データベース）

| 用語 | テーブル名 | 説明 |
|------|-----------|------|
| **Memo** | `memos` | ユーザーが投稿するメモ記事。タイトル・本文（Markdown）・画像を持つ |
| **User** | `users` | 登録ユーザー。通常ログインとGoogle OAuthの2種類が存在する |
| **Category** | `categories` | 記事に付与するカテゴリータグ。名前とカラーコードを持つ |
| **Favorite** | `favorites` | いいね。User と Memo の多対多を実現する中間エンティティ |
| **memo_categories** | `memo_categories` | Memo と Category の多対多の中間テーブル |

### リレーション図

```
User (1) ──< (N) Memo (N) >──< (N) Category
  │                │
  │(1)             │(1)
  │                │
  └──< (N) Favorite >──┘
```

---

## Blueprint（機能モジュール）

| Blueprint | URL接頭辞 | 説明 |
|-----------|----------|------|
| **public_bp** | `/` | トップページ。記事一覧・詳細表示・検索・カテゴリ絞り込み |
| **auth_bp** | `/auth` | 認証。ログイン・登録・ユーザー編集・削除・Google OAuth |
| **memo_bp** | `/memo` | マイページ。自分の記事のCRUD操作（要ログイン） |
| **favorite_bp** | `/favorite` | いいね機能。追加・削除（AJAX対応） |
| **fixed_bp** | `/fixed` | 固定ページ。STATIC_PAGES辞書で動的管理 |
| **docs_bp** | `/docs` | 成果物生成。ER図・仕様書等のCSV/画像出力 |
| **errors** | ― | エラーハンドリング。404ページ表示 |

---

## フォーム

| フォーム | 説明 |
|---------|------|
| **MemoForm** | 記事の投稿・編集フォーム。タイトル重複チェック（同一ユーザー内）あり |
| **LoginForm** | メールアドレス＋パスワードのログインフォーム。リメンバー機能付き |
| **SignUpForm** | ユーザー登録フォーム。LoginFormを継承し、ユーザー名・メール重複チェックを追加 |
| **EditUserForm** | ユーザー情報編集フォーム。パスワード変更・サムネイル変更・アカウント削除 |

---

## 機能用語

| 用語 | 定義場所 | 説明 |
|------|---------|------|
| **like_count** | views.py各所 | Favoriteレコード数から算出されるいいね件数 |
| **rank** | `Favorite.rank` | いいねのランク値（1〜5、NULLは未ランク） |
| **top10** | fixed/views.py, public/views.py | いいね数の多い順TOP10の記事リスト |
| **top5** | memo/views.py | ユーザーのランク付きいいねTOP5 |
| **recommended** | memo/views.py | カテゴリーが一致する他者の投稿（おすすめ） |
| **rand1** | public/views.py | 日替わりランダムのおすすめ記事1件 |
| **STATIC_PAGES** | fixed/views.py | 固定ページのキー→日本語タイトルの辞書。グローバルナビ・フッター生成に使用 |
| **save_upload** | utils/upload.py | ファイルアップロード関数。UUIDベースのファイル名を生成して保存 |
| **is_oauth_user** | User モデル | OAuthプロバイダー登録ユーザーかどうかの判定プロパティ |

---

## テンプレート用語

| 用語 | 説明 |
|------|------|
| **base.j2** | アプリ共通のベーステンプレート。グローバルナビとフッターを含む |
| **{blueprint}/base.j2** | 分野別ベーステンプレート（memo/base.j2、public/base.j2、fixed/base.j2） |
| **_formhelpers.j2** | フォーム描画マクロを定義するパーシャル |
| **_categories.j2** | カテゴリータグ選択コンポーネントのパーシャル |
| **layout/** | 共通レイアウトパーツ（head, mode, globalnav, sidemenu, footer） |
| **key_visual** | 各ページのヘッダー画像。`/static/images/fixed/<key>.jpg` で管理 |

---

## URL設計（主要エンドポイント）

```
GET  /                              → public.public_index
GET  /detail/<int:memo_id>          → public.detail
GET  /auth/                         → auth.login
POST /auth/                         → auth.login（認証処理）
GET  /auth/register                 → auth.register
GET  /auth/edit                     → auth.edit
POST /auth/delete                   → auth.delete
GET  /auth/oauth_login              → auth.oauth_login
GET  /auth/google/callback          → auth.auth_google
GET  /auth/api/check_userid         → auth.check_userid（API）
GET  /memo/                         → memo.index
GET  /memo/create                   → memo.create
POST /memo/update/<int:memo_id>     → memo.update
POST /memo/delete/<int:memo_id>     → memo.delete
POST /favorite/add/<int:memo_id>    → favorite.add
POST /favorite/remove/<int:memo_id> → favorite.remove_favorite
GET  /fixed/<page_name>             → fixed.static_page
```
