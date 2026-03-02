# ログ可視化機能 設計ドキュメント

**日付**: 2026-03-02
**Issue**: #2 ログの可視化
**担当**: admin Blueprint

---

## 受入条件

- 管理画面サイドメニューの「テスト網羅率状況」リンクの直下に「ログ可視化」リンクが表示される
- `/admin/logs` ページで過去1日（デフォルト）/ 3日 / 7日のログを切り替え表示できる
- ログは構造化テーブル（日時・レベル・モジュール・メッセージ）で表示される
- ERRORの件数・WARNINGの件数・INFO件数がサマリーカードで強調表示される
- JSによるレベルフィルター（ERROR / WARNING / INFO）が動作する

## 非目標

- リアルタイム更新（ポーリング・WebSocket）は実装しない
- ログのダウンロード機能は今回のスコープ外
- ローテーションされた旧ログ（app.log.1 等）の参照は対象外

---

## アーキテクチャ

### ファイル変更一覧

| ファイル | 変更内容 |
|---------|---------|
| `utils/logger.py` | ファイルハンドラーのレベルを `WARNING` → `INFO` に変更 |
| `admin/views.py` | `/admin/logs` ルート追加 |
| `templates/admin/logs.j2` | 新規テンプレート作成 |
| `templates/admin/sidemenu.j2` | ログ可視化リンク追加 |
| `templates/admin/sidemenu_nav.j2` | ログ可視化リンク追加 |

---

## バックエンド仕様

### ルート: `GET /admin/logs`

**クエリパラメータ**:
- `days`: `1`（デフォルト）/ `3` / `7`

**処理フロー**:
1. `logs/app.log` を読み込む（存在しない場合は空リストを返す）
2. 正規表現でパース: `\[(.+?)\] (\w+) \[(.+?)\] (.+)`
3. `days` パラメータで日時フィルタリング
4. 新しい順（降順）にソートしてテンプレートに渡す

**パース後データ構造**:
```python
{
  "datetime": "2026-03-02 14:23:10,123",
  "level": "ERROR",       # INFO / WARNING / ERROR / CRITICAL
  "module": "admin:128",
  "message": "500 Internal Server Error",
}
```

**テンプレート変数**:
- `logs`: パース済みログエントリのリスト
- `days`: 選択中の期間（int）
- `summary`: `{"error": N, "warning": N, "info": N, "total": N}`

---

## フロントエンド仕様

### レイアウト（`templates/admin/logs.j2`）

```
[ヘッダー] ログ可視化  [期間: 1日 | 3日 | 7日]
─────────────────────────────
[カード] ERROR N件  [カード] WARNING N件  [カード] INFO N件
─────────────────────────────
[フィルター] ALL | ERROR | WARNING | INFO
─────────────────────────────
[テーブルヘッダー] 日時 | レベル | モジュール | メッセージ
[行] 14:23:10 | ● ERROR | admin:128 | 500 Internal...
[行] 13:10:05 | ○ WARNING | auth:89  | Login failed...
[行] 12:00:01 | ○ INFO   | public:45| Page loaded
```

### デザイン規約

- カラーパレット: メインカラー `#234`、サブカラー `#212529`、明るい色 `#ccc`
- ボタン: `btn-outline-secondary` ベース（`btn-danger` 等は使用禁止）
- レベルバッジ:
  - `ERROR`: `badge bg-secondary` + 不透明度100%（目立たせる）
  - `WARNING`: `badge bg-secondary opacity-75`
  - `INFO`: `badge bg-secondary opacity-50`
- 行ハイライト: ERRORの行は `table-secondary` クラスで強調

### JS機能（`static/js/main.js` に追記）

- 期間セレクターボタン: クリックで `?days=N` のURLにページ遷移
- レベルフィルターボタン: クリックでテーブル行を `d-none` トグル（クライアントサイド）

---

## テスト方針

- 手動確認: ログファイルにサンプルログを書き込んで表示確認
- ログレベル変更後にアプリを再起動し、INFO ログが記録されることを確認
