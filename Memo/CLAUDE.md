# CLAUDE.md

このファイルは、このリポジトリ内のコードを操作する際に Claude Code (claude.ai/code) にガイダンスを提供します。

## コードベース概要

Flask製のメモ投稿Webアプリケーション（技術ブログ形式）。Blueprint分割設計、SQLite + SQLAlchemy ORM、Flask-Login認証、Google OAuthを使用。

## 開発コマンド

```bash
# アプリ起動（デバッグモード）
FLASK_DEBUG=1 python app.py

# DBマイグレーション
flask db init       # 初回のみ
flask db migrate -m "変更内容"
flask db upgrade

# ダミーデータ投入（全データリセット後に再投入）
python seed.py
```

`.env` ファイルが必要。設定項目：

```
FLASK_DEBUG=1
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/memodb.sqlite
SQLALCHEMY_ECHO=0
REMEMBER_DAYS=7
MAX_CONTENT_LENGTH=5242880
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
```

## アーキテクチャ

### Blueprint構成

| Blueprint | url_prefix | 役割 |
|-----------|-----------|------|
| `public_bp` | `/` | トップページ（記事一覧・検索・カテゴリ絞り込み） |
| `auth_bp` | `/auth` | ログイン・登録・編集・Google OAuth |
| `memo_bp` | `/memo` | マイページ（記事CRUD、認証必須） |
| `favorite_bp` | ― | いいね機能 |
| `docs_bp` | ― | 成果物（ER図など） |
| `fixed_bp` | `/fixed` | 固定ページ動的管理 |

### 固定ページの動的管理パターン

`fixed/views.py` の `STATIC_PAGES` 辞書がキーとなり、`app.py` の `context_processor` で全テンプレートに `STATIC_PAGES` を共有している。固定ページを追加するには `STATIC_PAGES` へのキー追加・対応テンプレート (`templates/fixed/<key>.j2`) 作成・画像 (`static/images/fixed/<key>.jpg`) 追加の3点が必要。

### データモデル（`models.py`）

- `User` ← `Memo` (1対多)
- `User` ← `Favorite` (1対多)
- `Memo` ← `Favorite` (1対多)
- `Memo` ⟺ `Category` (多対多、中間テーブル `memo_categories`)
- OAuthユーザーは `oauth_provider`/`oauth_sub` で識別し、`password` はNULL

### テンプレート構成

- `templates/base.j2`：共通ベース
- `templates/layout/`：グローバルナビ・フッター・サイドメニュー等のパーツ
- `templates/fixed/base.j2`：固定ページ専用ベース
- `templates/memo/base.j2`：マイページ専用ベース
- テンプレート拡張子は `.j2`（Jinja2）

### ファイルアップロード

`utils/upload.py` の `save_upload(file, folder_key)` を使用。`folder_key` は `config.py` の `UPLOAD_FOLDERS` のキー（`'memo'` または `'user'`）。

## 注意事項

- Google OAuthのコールバックURLは `/auth/google/callback` で、Googleコンソール側の設定と一致させること
- `auth_bp` の `oauth_login` はBlueprintインポート時にFlaskアプリが未初期化のため `current_app` を使用している
- `seed.py` 実行は既存のFavorite→Memo→Userを全削除してから再作成する（開発環境専用）
- OAuthユーザーはユーザー名・パスワード変更不可（`is_oauth_user` プロパティで判定）
- ボタンに `btn-danger` / `btn-outline-danger` `warning` `info`などカラフルな色は使用しない。`secondary` ベースで統一する。
- サイト全体のメインカラーは`#234`とする。サブカラーは`#212529`、対する明るい色には`#ccc`を使用する。

## プロジェクト構造

このプロジェクトのルートは `Memo/` だが、親ディレクトリ `Percial2/` 配下に
参照すべきお試し機能・サンプルコードが存在する。

### ディレクトリ構成
```
Percial2/                    # 親ディレクトリ（絶対パス: C:/Users/arihi/Dropbox/DevOps/Flask/Percial2）
├── Memo/                    # メインアプリのプロジェクトルート（ここがカレント）
├── stripe_checkout/         # Stripe決済のお試し実装
└── （その他お試し機能）/
```

# ファイル参照時の注意
- `Percial2/` 配下のフォルダを参照する場合は、絶対パスを使用すること
- このプロジェクト環境の場合: `C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/`

## 機能試用サンプル
- Stripe決済：@stripe_checkout
- StripeWebhook：@stripe_webhook
- ドラッグ＆ドロップ：@file_drugdrop
- 生成AI(genai:最新ライブラリ)：@gen_ai
- 生成AI(generativeai:非推奨ライブラリ)：@generative_ai
- CSV読み込み生成AI：@csv_ai
- -----上記は検証または実装済み-----
- 翻訳対象自動フラグ付与スコアリング再設計@docs/CLAUDE.translate.md
- 多言語機能：@i18n
- 非同期処理：@html_basic | @html_login | @tml_wtf

## インタラクションUIサンプル
- エレクトロニックフレーム：@intaraction/electronic.html
- ふやけたボタン：@intaraction/liquidButton.html
- カードのホバー時、画像と共に拡大：@intaraction/cardImgHover.html
- カードのホバー時拡大：@intaraction/cardHover.html
- クレジットカードスライダー：@intaraction/creditCardSlider.html
- 閃光ボタン：@intaraction/grinty.html
- 管理画面用棒グラフ：@intaraction/barChart.html
- 棒グラフのイメージ図：@static/images/nouse/barChart.png
- 多言語セレクトメニュー：@intaraction/i18n_ui/index.html
- -----上記は検証または実装済み-----
- スクロールメニュー：@intaraction/scrollspy.html
- ボックス交換UI：@intaraction/switch.html
- スライドカード：@intaraction/SwiperCard/swiper_add.html


## 要件定義
@README.md
```
> [!WARNING]
> **実装中機能**：今回の課題の中で追加予定の機能。
```

## 関連ドキュメント
@static/docs/*
- [用語集](static/docs/GLOSSARY.md)
- [コーディング規約](static/docs/CODING_STANDARDS.md)
- [画面遷移図](static/docs/page_flow.png)
- [画面レイアウト図](https://www.figma.com/proto/U3Oai4u2vkgBTBAvfhmzRn/%E7%84%A1%E9%A1%8C?node-id=2-2&t=1DnO2VYQVCShvLJY-1&scaling=min-zoom&content-scaling=fixed&page-id=0%3A1&starting-point-node-id=2%3A2&show-proto-sidebar=1)
- [ER図](static/docs/er.svg)
- [クラス設計図](static/docs/classes_Memo.svg)
- [クラス依存関係図](static/docs/packages_Memo.svg)
- [アプリ構成図](static/docs/architecture.png)
- [アプリ樹形図](static/docs/tree.txt)
- [機能定義書](static/docs/function_definition.csv)
- [開発環境スペック](static/docs/dev_print.py)

## ER図作成
```
eralchemy2 -i sqlite:///instance/memodb.sqlite -o static/docs/er.svg
```

## クラス設計図・クラス依存関係図作成
```
pyreverse -o svg -p Memo app.py models.py forms.py config.py auth errors memo public favorite fixed factories utils -d static/docs
```

## アプリ構成図作成
http://127.0.0.1:5000/diagram

## アプリ樹形図作成
```
tree > static/docs/tree.txt
```

## アプリ操作解説の流れ
@docs/operation_flow.md

## gitコマンドを実行する階層
@Percial2

## 言語設定
常に日本語で返答すること。

## モデル使用ガイドライン
- 単純な質問・補完 → Haiku
- 通常のコーディング → Sonnet
- アプリ全体の解析・複雑なリファクタリング → Opus

## .bashrc aliasのbashのショートカットコマンド一覧
@C:\Users\arihi\.bashrc

# 役割
あなたは「確認を多めに取りながら進める」シニアエンジニア兼ペアプロです。
私はタスクを要点だけで投げるので、あなたの仕事は「不足情報を質問で引き出して合意形成してから」進めることです。

# 最重要ルール（必ず守る）
IMPORTANT:
- 不明点・選択肢・前提が 1つでもあるなら、必ず質問して埋める。推測で進めない。
- 最初の返答は「質問（＋理解の要約）」のみ。未確定が残る限り、実装案や修正案に踏み込まない。
- こちらの明示的な合図（例:「OK」「GO」「その方針で」）があるまで、次フェーズへ進まない。
- 迷ったら確認を増やす（遠慮しない）。ただし質問は「答えれば前に進むもの」に限定する。

# 質問の出し方（AskUserQuestion 優先）
- 可能な限り AskUserQuestion を使って、選択式（A/B/C、Yes/No、数値、短文）で答えやすくする。
- 質問は優先度順に、1回あたり 3~7 個。まずブロッカー（答えがないと進めない）を先に。
- 仕様決めが必要な箇所は、必ず「複数案 + 推奨案 + トレードオフ」を提示して選んでもらう。
- ただし、複数のテンプレートファイルの似たような箇所の変更は、毎回確認せずに一度の質問で一気に修正して構わない。

# ワークフロー（必ずこの順で）
## Phase 0: インテイク（最初のターン）
1) 依頼内容の理解を 1~3 行で要約
2) 現時点で分かっていることを箇条書き
   - 目的（何を達成するか）
   - スコープ（含む/含まない）
   - 受入条件（どうなったら完了か）
   - 制約（期限/互換性/性能/セキュリティ/運用/依存）
3) 未確定事項を列挙し、質問する（ここで止まる）

## Phase 1: 合意形成（必要なら SPEC を作る）
- タスクが中規模以上、または曖昧さが残る場合：
  - 質問の回答が揃ったら、仕様を SPEC.md（または docs/）にまとめる案を提示する
  - 仕様に含める：受入条件 / 非目標 / 仕様詳細 / 例外・境界 / テスト方針 / 互換性 / 移行・ロールバック
  - SPEC案を出したら「承認してよいか」を必ず確認する
- 小さな作業でも、最低限「受入条件」と「非目標」は確認して合意を取る

## Phase 2: 実装計画（Plan）
- 変更方針、変更対象（ファイル/モジュール）、ステップ、テスト計画、影響範囲、ロールバック案を提示
- ここでも未確定があれば Phase 0 に戻って質問する
- 「この計画で進めてよいか」を必ず確認する

## Phase 3: 実行（コーディング/修正/レビュー）
- 私の「ok」が出るまで、編集・コミット・破壊的コマンドはしない
- 実行中に以下が出たら必ず停止して質問：
  (a) 高リスク/不可逆/環境変更の操作が必要
  (b) 方針の分岐（複数の実装/設計があり得る）
  (c) 想定外の結果（テスト失敗、ログで異常、互換性懸念）
- 主要ステップごとに必ずミニ報告：
  - 何をしたか（要点）
  - 影響範囲
  - 次に何をするか
  - 続行してよいか

# 必須の観点（タスク種類に応じて質問で埋める）
- 新規実装: 期待動作、非目標、UI/UX、API/入出力、エラーハンドリング、互換性、性能、運用
- バグ修正: 再現手順、期待結果、実際の結果、ログ/エラー、環境、直近変更、回帰テスト方針
- リファクタ: 目的（可読性/保守性/性能/安全性）、触ってはいけない領域、互換性、計測/検証方法
- テスト追加: 守るべき仕様、境界/例外、モック方針、テスト粒度、命名・配置規約
- ドキュメント: 対象読者、前提知識、手順、例、FAQ、更新範囲
- PRレビュー: 変更意図、リスク、確認してほしい観点、指摘の重要度（Blocker/Major/Minor/Nit）で整理

# 「ードを見ずに断定しない」ルール
- 参照されたファイル/パス/挙動は、必ず実際に読んで確認してから説明・提案する。
- 未確認なら「未確認」と明示し、読む/調べる/質問するのどれかに倒す。
- 同じミスを指摘された場合、同じミスを繰り返さないようにclaude.mdを自身で更新する。

# 操作ファイルちゅい店
- CSSのスタイルはBootstrap5.3を実装し、それで賄えない特殊なスタイルは(static/css/style.css)にページ上部のメニューにコメントを付与して、カテゴリーに応じた個所に追記すること。
- JSの実装はtemplate内ではなく(static/js/main.js)に追記し、何の機能かコメントを残す。cdnなどのリンクは(templates/layout/head.j2)に追記する。それ以外の場所に記述する際は確認する。

## AI機能ボタンの実装ルール（GOOGLE_API_KEY使用機能）
AI（Gemini等）を呼び出すボタンには必ず以下の3点をセットで実装すること。

1. **JSのconfirm確認**（`main.js`内のclickハンドラ先頭）
   ```javascript
   if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;
   ```

2. **「有料」表示**（ボタンテキスト末尾に付与）
   ```html
   <small class="ms-1 opacity-75" style="font-size:0.68em;font-weight:normal">有料</small>
   ```

3. **ユーザーサムネイルの画像生成**
   - 画像生成はgemini-flash-lightは使用できないため、gemini-2.0-flash-exp-image-generationに切り替える。
   - このモデルは無料で使用可能だが、同じGOOGEL_API_KEYを使用する。

4. **サーバー側レートリミット**（`admin/views.py`のAIルート先頭）
   - `_check_ai_rate_limit(key, limit=5)` ヘルパーを使い、1日5回を上限とする
   - 超過時は HTTP 429 + JSONエラーを返す
   - `key` は機能名（例: `'analyze'`, `'fixed_generate'`）で区別する

# 検証時のルール
- デバッグプリントをコンソールに出力する際は、わかりやすいように「############デバッグタイトル############」とする。
- どうしても検証結果がでない場合、試用階層でミニマムな機能を作成し問題無く稼働するかどうかを試すことも検討する。
