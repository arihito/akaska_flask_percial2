# ロギング・エラー通知メール 設計書

**日付**: 2026-02-28
**ステータス**: 承認済み

---

## 目的

- アプリケーションのエラーを `logs/app.log` に永続化する
- 500系サーバーエラー発生時に管理者へメール通知する

## 非目標

- 400系（404等）はメール通知しない
- 非同期キュー（Celery等）は使用しない
- 外部ログ収集サービス（Sentry等）は導入しない

---

## アーキテクチャ

```
utils/logger.py
  └── init_logger(app)
        ├── RotatingFileHandler  → logs/app.log（10MB × 最大5世代）
        ├── StreamHandler        → コンソール（DEBUGモード時のみ）
        └── SMTPHandler          → Gmail → MAIL_USERNAME（本番のみ）

app.py
  └── create_app()
        └── init_logger(app)  ← 追加1行のみ
```

---

## 変更ファイル一覧

| ファイル | 変更種別 | 内容 |
|----------|---------|------|
| `utils/logger.py` | 新規作成 | `init_logger(app)` 関数 |
| `app.py` | 修正 | `init_logger(app)` 呼び出し追加 + 500エラーハンドラー追加 |
| `.gitignore` | 修正 | `logs/` を追加 |

---

## 詳細仕様

### `utils/logger.py`

- `RotatingFileHandler`: `logs/app.log`、最大10MB、バックアップ5世代
  - `logs/` ディレクトリが存在しない場合は自動作成
- `StreamHandler`: コンソール出力（`app.debug == True` のときのみ追加）
- `SMTPHandler`: `app.debug == False`（本番）のときのみ有効化
  - ログレベル: `ERROR` 以上
  - 送信先: `MAIL_USERNAME`
  - 件名: `[Flask tech blog] サーバーエラーが発生しました`
  - 送信元・認証情報: `config.py` の `MAIL_*` 設定を使用

### ログフォーマット

```
[2026-02-28 12:00:00,123] ERROR [utils.logger:45] エラーメッセージ
```

### ログレベル方針

| レベル | 用途 | メール通知 |
|--------|------|------------|
| DEBUG | SQLクエリ等（開発時） | なし |
| INFO | リクエスト情報 | なし |
| WARNING | 軽微な異常 | なし |
| ERROR / CRITICAL | 500系サーバーエラー | あり（本番のみ） |

---

## 受入条件

1. `logs/app.log` にERROR以上のログが記録される
2. 開発時（`FLASK_DEBUG=1`）はコンソールにもログが出力される
3. 本番環境（`FLASK_DEBUG=0`）でサーバーエラー発生時に `MAIL_USERNAME` 宛にメールが届く
4. `logs/` ディレクトリはgit管理外になっている

---

## 互換性

- 既存のBlueprint・テンプレート・DB構造への変更なし
- テスト環境では `app.testing = True` のため SMTPHandler は無効

---

## ロールバック

`utils/logger.py` を削除し、`app.py` の変更を元に戻すのみ。DBマイグレーション不要。
