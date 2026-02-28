# テスト自動化 設計ドキュメント

作成日: 2026-02-27

## 目的

GitHub Actions を使って Push 時に自動テストを実行し、テスト失敗時は main への Push をブロックする CI/CD パイプラインを構築する。

## 非目標

- E2E テスト（Playwright 等）は対象外
- 本番 PostgreSQL を使ったテストは対象外（SQLite インメモリで代替）
- テストカバレッジ 100% の達成は非目標

## アプローチ

**pytest + pytest-flask + SQLite インメモリ + factory_boy**

既存の `factory_boy` を活用し、テスト専用の SQLite インメモリ DB を使用する。

## ファイル構成

```
Memo/
├── tests/
│   ├── conftest.py       # pytest フィクスチャ（app, client, db, ユーザー）
│   ├── test_models.py    # 単体テスト（モデルの制約・バリデーション）
│   ├── test_auth.py      # 結合テスト（ログイン/ログアウト/アクセス制限）
│   ├── test_memo.py      # 結合テスト（投稿CRUD・認可チェック）
│   └── test_public.py   # 結合テスト（公開ページのHTTPレスポンス）
├── pytest.ini            # pytest 設定
└── requirements.txt      # pytest, pytest-flask, pytest-cov を追加
```

## conftest.py 設計

```python
# テスト設定のポイント
# - TESTING=True
# - DATABASE_URL: sqlite:///:memory:（インメモリDB）
# - WTF_CSRF_ENABLED=False（フォームテスト時のCSRF無効化）
# - SECRET_KEY: テスト用固定値

# フィクスチャ
# - app: セッションスコープ（全テストで1つのappインスタンス）
# - db: functionスコープ（各テスト後にロールバック）
# - client: Flask テストクライアント
# - auth_client: ログイン済みテストクライアント
# - test_user: factory_boy で生成したテストユーザー
```

## テストケース一覧

### test_models.py（単体テスト）
| テストケース | 検証内容 |
|---|---|
| `test_password_hashing` | パスワードがハッシュ化されて保存される |
| `test_memo_title_max_length` | タイトル50文字超でバリデーションエラー |
| `test_category_unique_name` | 同名カテゴリーが2件目で IntegrityError |
| `test_user_email_unique` | 同メールアドレスが2件目で IntegrityError |

### test_auth.py（結合テスト）
| テストケース | 検証内容 |
|---|---|
| `test_login_success` | 正しい認証情報 → 302リダイレクト |
| `test_login_wrong_password` | 誤ったパスワード → 200（エラーメッセージ含む） |
| `test_logout` | ログアウト後 → ログインページへリダイレクト |
| `test_memo_requires_login` | 未ログインで `/memo/` → `/auth/login` へリダイレクト |

### test_memo.py（結合テスト）
| テストケース | 検証内容 |
|---|---|
| `test_create_memo` | 投稿作成POST → 302 + DB に1件追加 |
| `test_update_memo_own` | 自分の投稿を編集 → 302 |
| `test_update_memo_other` | 他人の投稿を編集しようとする → 403 |
| `test_delete_memo` | 投稿削除 → DB から1件減る |

### test_public.py（結合テスト）
| テストケース | 検証内容 |
|---|---|
| `test_top_page` | `GET /` → 200 |
| `test_search` | `GET /?q=test` → 200 |
| `test_category_filter` | `GET /?category=1` → 200 |
| `test_detail_page` | `GET /detail/<id>` → 200 |

## GitHub Actions 設計

```yaml
# .github/workflows/test.yml
name: CI Test

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
      - run: pip install -r Memo/requirements.txt
      - run: pytest --cov=. --cov-report=term-missing
        working-directory: Memo
        env:
          SECRET_KEY: test-secret-key
          DATABASE_URL: sqlite:///:memory:
          GOOGLE_CLIENT_ID: dummy
          GOOGLE_CLIENT_SECRET: dummy
```

## 追加パッケージ

```
pytest==8.x
pytest-flask==1.3.x
pytest-cov==6.x
```

## 受け入れ条件

- [ ] `pytest` をローカルで実行して全テストがパスする
- [ ] GitHub Actions で Push 時に自動テストが実行される
- [ ] テスト失敗時に GitHub Actions が `failure` になる
- [ ] カバレッジレポートがコンソールに出力される

## ロールバック

テスト追加は既存コードに非破壊的。`tests/` ディレクトリと `pytest.ini` を削除すれば元に戻せる。
