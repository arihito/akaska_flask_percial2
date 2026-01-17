# タスクリスト

![](https://img.shields.io/badge/Flask-2.3.3~3.12.5-ff6699.svg)
![](https://img.shields.io/badge/Python-3.1.2-006400.svg)
![](https://img.shields.io/badge/Werkzeug-3.1.4-666666.svg)

## 環境構築

- 作業環境にて以下をコンソールにコピペし実行

```
mkdir -p tasklist/templates && touch tasklist/app.py tasklist/templates/index.j2 && cd tasklist && pip install flask Flask-SQLAlchemy pytz
```

- app.pyとtemplates/index.j2の各コードを右上のコピーボタンから一括コピーしてファイルに貼り付ける。

  - [app.py](https://github.com/arihito/akaska_flask_percial2/blob/main/tasklist/app.py)
  - [index.j2](https://github.com/arihito/akaska_flask_percial2/blob/main/tasklist/templates/index.j2)

- 以下をコンソールにコピペし実行

```
flask db init && flask db migrate && flask db upgrade && flask run
```

## 機能操作確認

> [!NOTE]
> **基本要件**：最低限実装しておく機能。

- タスクの追加 x 5
- タスクの完了
- タスクを戻す

> [!NOTE]
> **追加要件**：新たに自身でチャレンジしていく機能。

- タスクの追加画面統一
- タスクの削除
- タスクの全件削除

- タスクの一括完了
- タスクの一括戻す

- タスクの検索絞り込み

- タスクの日時表示(マイグレート更新)
- タスクの新しい順に並び替え
- タスクの古い順に並び替え


## 学習のコツ

- [**フレームワーク3周**](https://www.google.com/search?q=%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0%E3%83%AF%E3%83%BC%E3%82%AF3%E5%91%A8&oq=%E3%83%95%E3%83%AC%E3%83%BC%E3%83%A0%E3%83%AF%E3%83%BC%E3%82%AF3%E5%91%A8&aqs=chrome..69i57j0i512i546j0i751j0i512i546l3.1069j0j7&sourceid=chrome&ie=UTF-8)
- **CRUDまでが命綱**：CRUDまでチンプンカンプンでも、それさえ習得できたらアプリ開発のイメージが付くので、最短のCRUDを3回模写して定着させる。
- **何でもAI**：機能実装はHTMLから追加し過去のメソッドをコピペ改造する。後はAIに聞く。エラーが出てもコードを丸投げして「問題点があれば指摘してください」でデバッグ可能。コードの仕組みや概念がわからなかったら、そのままの疑問をAIに投げる。些細な疑問も全て投げる。
