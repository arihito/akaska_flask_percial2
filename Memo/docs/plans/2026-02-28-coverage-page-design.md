# テスト網羅率ページ 設計ドキュメント

作成日: 2026-02-28

## 目的

管理画面にテストカバレッジの確認ページを追加する。ページ表示は即時で、任意の「テスト実行」ボタンで最新データに更新できる。

## 非目標

- ページアクセスのたびに自動でpytestを実行しない
- E2Eテストや外部CI結果の表示は対象外

## アーキテクチャ

### エンドポイント

| ルート | メソッド | 役割 |
|---|---|---|
| `/admin/coverage` | GET | ページ表示（coverage.json を読み込むだけ、即時） |
| `/admin/coverage/run` | POST | pytest を実行して coverage.json を生成、JSON で結果を返す |

### データフロー

```
ページアクセス（即時）
  → coverage.json が存在すれば読み込んで表示
  → 存在しなければ「未実行」メッセージを表示

「テスト実行」ボタンをクリック
  → AJAX POST /admin/coverage/run
  → サーバー: pytest --cov=. --cov-report=json を subprocess 実行
  → ローディングスピナー表示（数秒〜十数秒）
  → 完了後: 結果 JSON を返してページDOMを更新
```

## 表示内容

- 合計カバレッジ（大きな数字）
- ファイル別テーブル（ファイル名 / ステートメント数 / カバレッジ% / プログレスバー）
- 最終実行日時（coverage.json の更新日時から取得）
- 「テスト実行」ボタン（クリックでAJAX実行、スピナー付き）

## ファイル

- Modify: `admin/views.py` — `coverage`, `coverage_run` ルート追加
- Create: `templates/admin/coverage.j2` — `admin/base.j2` 継承
- Modify: `templates/admin/sidemenu.j2` — メニューのhrefを `url_for('admin.coverage')` に更新
- Modify: `static/js/main.js` — テスト実行ボタンのAJAXハンドラ追加

## 受け入れ条件

- [ ] `/admin/coverage` が既存の coverage.json を読み込んで即時表示される
- [ ] coverage.json がない場合は「まだ実行されていません」と表示される
- [ ] 「テスト実行」ボタンを押すと pytest が実行され、完了後に結果が更新される
- [ ] 実行中はスピナーが表示される
- [ ] admin/base.j2 のレイアウトに従っている

## ロールバック

- `admin/views.py` の2ルートを削除
- `templates/admin/coverage.j2` を削除
- `sidemenu.j2` のhrefを空文字に戻す
