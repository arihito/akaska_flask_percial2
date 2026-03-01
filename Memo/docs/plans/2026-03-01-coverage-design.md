# テストカバレッジ改善 設計書

**日付**: 2026-03-01
**ステータス**: 承認済み

---

## 目的

- `factories/`・`seed.py`・`admin/`・`docs/`・`utils/ai_*.py` をカバレッジ計測から除外する
- 残るコアモジュール（auth/memo/public/favorite/fixed views + models + forms + utils/upload + utils/logger）のカバレッジを **90% 以上** に引き上げる

## 非目標

- `admin/views.py`（829行）のテスト追加は行わない
- `docs/views.py`（ER図・diagram生成）のテスト追加は行わない
- `utils/ai_*.py`（AI機能）のテスト追加は行わない
- `admin/webhook.py`（Stripe Webhook）のテスト追加は行わない

---

## アーキテクチャ

```
.coveragerc           ← 新規作成（除外設定 + fail_under=90）
pytest.ini            ← --cov-fail-under=40 を --cov-fail-under=90 に変更

tests/
  test_auth.py        ← 拡充（OAuth/register/logout/edit）
  test_memo.py        ← 拡充（create/update/delete/validation）
  test_public.py      ← 拡充（search/category/pagination）
  test_favorite.py    ← 新規作成（toggle/auth-required）
  test_fixed.py       ← 新規作成（固定ページ表示）
  test_forms.py       ← 新規作成（バリデーション）
  test_upload.py      ← 新規作成（ファイルアップロード）
  test_logger.py      ← 拡充（SMTPハンドラー）
```

---

## 対象ファイルと目標

| ファイル | 現状 | 目標 | 主な追加テスト |
|---------|------|------|--------------|
| `auth/views.py` | 44% | ≥90% | register成功/失敗, logout, プロフィール編集, OAuth関連 |
| `favorite/views.py` | 40% | ≥90% | いいねトグル, 未ログイン時リダイレクト |
| `fixed/views.py` | 50% | ≥90% | 各固定ページのGET |
| `forms.py` | 75% | ≥90% | バリデーション境界値（パスワード強度等） |
| `memo/views.py` | 67% | ≥90% | create/update/delete, 画像なし, バリデーション失敗 |
| `public/views.py` | 72% | ≥90% | 検索, カテゴリーフィルター, ソート |
| `utils/logger.py` | 78% | ≥90% | SMTPハンドラー初期化（non-debug環境） |
| `utils/upload.py` | 33% | ≥90% | ファイルタイプ検証, 保存先パス生成 |

---

## 除外設定（`.coveragerc`）

```ini
[run]
omit =
    factories/*
    seed.py
    admin/*
    docs/*
    utils/ai_*.py

[report]
fail_under = 90
```

---

## 受入条件

1. `.coveragerc` が存在し、対象外ファイルが除外されている
2. `pytest.ini` の `--cov-fail-under` が 90 になっている
3. `conda run -n flask2_env pytest tests/ -v` が全てPASSする
4. カバレッジレポートで **TOTAL ≥ 90%** が表示される

---

## 互換性

- 既存の26件テストはすべてそのまま維持
- DB・テンプレート・Blueprintへの変更なし
- `conftest.py` の fixture を最大限再利用

---

## ロールバック

`.coveragerc` を削除し、`pytest.ini` の `--cov-fail-under` を 40 に戻すのみ。
