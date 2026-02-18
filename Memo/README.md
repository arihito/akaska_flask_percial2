
<img src="https://raw.githubusercontent.com/arihito/akaska_flask_percial2/refs/heads/main/Memo/static/images/fixed/keyvisual.jpg" alt="" width="" height="">

![](https://img.shields.io/badge/VSCode-003864?style=for-the-badge&logo=visual%20studio%20code&logoColor=white)![](https://img.shields.io/badge/conda-225500.svg?&style=for-the-badge&logo=anaconda&logoColor=white)![](https://img.shields.io/badge/Python-333355?style=for-the-badge&logo=python&logoColor=blue)![](https://img.shields.io/badge/Flask-111122?style=for-the-badge&logo=flask&logoColor=white)![](https://img.shields.io/badge/Sqlite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)![](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)![](https://img.shields.io/badge/GIT-942C10?style=for-the-badge&logo=git&logoColor=white)![](https://img.shields.io/badge/HTML5-431F26?style=for-the-badge&logo=html5&logoColor=white)![](https://img.shields.io/badge/Bootstrap-361D5C?style=for-the-badge&logo=bootstrap&logoColor=white)<br>
![](https://img.shields.io/badge/JavaScript-323330?style=for-the-badge&logo=javascript&logoColor=F7DF1E)![](https://img.shields.io/badge/%3C/%3E%20htmx-1D4257?style=for-the-badge&logo=mysl&logoColor=white)![](https://img.shields.io/badge/Font_Awesome-225600?style=for-the-badge&logo=fontawesome&logoColor=white)![](https://img.shields.io/badge/ChatGPT-24333c?style=for-the-badge&logo=openai&logoColor=white)![](https://img.shields.io/badge/Google%20Gemini-3E2542?style=for-the-badge&logo=googlegemini&logoColor=white) ![](https://img.shields.io/badge/Flask_tech_blog-v1.0.1-222243.svg)

<img src="https://raw.githubusercontent.com/arihito/akaska_flask_percial2/refs/heads/main/Memo/static/images/other/capture.png" alt="" width="800" height="">
<img src="https://raw.githubusercontent.com/arihito/akaska_flask_percial2/refs/heads/main/Memo/static/images/other/admin.png" alt="" width="800" height="">

<hr width="800">

> [!IMPORTANT]
> **樹形図**：アプリケーション内の主要なディレクトリやファイル(__pycache__、__init__.py、静的画像等は除く)

<details>
<summary>樹形図詳細</summary>
![](https://img.shields.io/badge/TreeGraph_20260209-222243.svg)
<pre><code>
[ Memo ]
├─ 📄README.md
├─ 📁__pycache__
├─ 📄app.py
├─ 📁auth
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📄config.py
├─ 📁data
│   └─ 📁sample_articles
│       ├─ 📄api_001.md
│       ├─ 📄auth_001.md
│       ├─ 📄api_002.md
│       ├─ 📄basic_001.md
│       ├─ 📄basic_002.md
│       ├─ 📄crud_001.md
│       ├─ 📄crud_002.md
│       ├─ 📄package_001.md
│       ├─ 📄ui_001.md
│       └─ 📄ui_002.md
├─ 📁errors
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📁factories
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   ├─ 📄body_factory.py
│   └─ 📄user_factory.py
├─ 📁favorite
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📁fixed
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📄forms.py
├─ 📁instance
│   └─ 📄memodb.sqlite
├─ 📄libraries.txt
├─ 📁memo
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📁migrations
│   ├─ 📄README
│   ├─ 📁__pycache__
│   ├─ 📄alembic.ini
│   ├─ 📄env.py
│   ├─ 📄script.py.mako
│   └─ 📁versions
├─ 📄models.py
├─ 📁public
│   ├─ 📄__init__.py
│   ├─ 📁__pycache__
│   └─ 📄views.py
├─ 📄seed.py
├─ 📁static
│   ├─ 📁css
│   │   └─ 📄style.css
│   ├─ 📁images
│   │   ├─ 📁fixed
│   │   ├─ 📁memo
│   │   ├─ 📁nouse
│   │   ├─ 📁other
│   │   └─ 📁user
│   └─ 📁js
│       └─ 📄main.js
├─ 📁templates
│   ├─ 📁auth
│   │   ├─ 📄_formhelpers.j2
│   │   ├─ 📄edit.j2
│   │   ├─ 📄login.j2
│   │   └─ 📄register.j2
│   ├─ 📄base.j2
│   ├─ 📁errors
│   │   └─ 📄404.j2
│   ├─ 📁fixed
│   │   ├─ 📄base.j2
│   │   ├─ 📄copyright.j2
│   │   ├─ 📄crud.j2
│   │   ├─ 📄deploy.j2
│   │   ├─ 📄disclaimer.j2
│   │   ├─ 📄drop.j2
│   │   ├─ 📄help.j2
│   │   ├─ 📄htmx.j2
│   │   ├─ 📄i18n.j2
│   │   ├─ 📄jwt.j2
│   │   ├─ 📄legal.j2
│   │   ├─ 📄oauth.j2
│   │   ├─ 📄paging.j2
│   │   ├─ 📄policy.j2
│   │   ├─ 📄refactor.j2
│   │   ├─ 📄stripe.j2
│   │   ├─ 📄terms.j2
│   │   ├─ 📄twofactor.j2
│   │   └─ 📄upload.j2
│   ├─ 📁layout
│   │   ├─ 📄footer.j2
│   │   ├─ 📄globalnav.j2
│   │   ├─ 📄head.j2
│   │   ├─ 📄mode.j2
│   │   └─ 📄sidemenu.j2
│   ├─ 📁memo
│   │   ├─ 📄_formhelpers.j2
│   │   ├─ 📄base.j2
│   │   ├─ 📄create.j2
│   │   ├─ 📄index.j2
│   │   └─ 📄update.j2
│   └─ 📁public
│       ├─ 📄aside.j2
│       ├─ 📄detail.j2
│       └─ 📄index.j2
├─ 📄tree.txt
└─ 📁utils
    ├─ 📁__pycache__
    │   └─ 📄upload.cpython-310.pyc
    └─ 📄upload.py
</code></pre>
</details>

<hr width="800">

> [!TIP]
> **使用ライブラリ**：アプリケーション内で追加したパッケージ群。

<details>
<summary>ライブラリ一覧</summary>
![](https://img.shields.io/badge/PackageList_20260209-222243.svg)
<pre><code>
Package                      Version
---------------------------- -----------
alembic            1.18.3
Authlib            1.6.6
blinker            1.9.0
certifi            2026.1.4
cffi               2.0.0
charset-normalizer 3.4.4
click              8.3.1
colorama           0.4.6
cryptography       46.0.4
dnspython          2.8.0
email-validator    2.3.0
factory_boy        3.3.3
Faker              40.1.2
Flask              2.3.3
Flask-DebugToolbar 0.16.0
Flask-Login        0.6.3
Flask-Migrate      4.1.0
Flask-SQLAlchemy   3.1.1
Flask-WTF          1.2.2
greenlet           3.3.1
idna               3.11
itsdangerous       2.2.0
Jinja2             3.1.6
Mako               1.3.10
Markdown           3.10.1
MarkupSafe         3.0.3
pip                25.3
pycparser          3.0
python-dotenv      1.2.1
pytz               2025.2
requests           2.32.5
setuptools         80.9.0
SQLAlchemy         2.0.46
tomli              2.4.0
typing_extensions  4.15.0
tzdata             2025.3
urllib3            2.6.3
Werkzeug           2.3.8
wheel              0.45.1
WTForms            3.2.1
</code></pre>
</details>

<hr width="800">

> [!NOTE]
> **要件定義**：追加済み機能要件。

<details>
<summary>実装済み機能一覧</summary>
<!-- START_TERM -->
<ul class="term">
  <li>
    環境構築
    <ul>
      <li>Flaskデバッガー</li>
      <li>VSCode：コード整形・スニペット</li>
      <li>bashエイリアス</li>
    </ul>
  </li>
  <li>投稿のCRUD実装
      <ul>
        <li>Bootstrapでトップはヘッダーナビ、管理画面は再度ナビにテンプレートを分割しレイアウトを変更</li>
        <li>テーブル行クリックで詳細画面に移動し、内包ボタンとの<code>衝突回避</code></li>
        <li>ダミーの記事本文ボリュームを増やすため1000字程度で別ファイルにMarkdown形式で10件作成</li>
      </ul>
  </li>
  <li>
    ユーザログイン認証
    <ul>
      <li>未ログインのアクセス制限</li>
      <li>ユーザ名は同姓同名を考慮し一意を解除し、メールアドレスを一意でログイン判定の基準に変更</li>
      <li><code>React</code>を使用したユーザーID変更時の<code>リアルタイムバリデーション</code></li>
    </ul>
  </li>
  <li>認可（自身の投稿のみにCRUDを制限）</li>
  <li><code>Google OAuth</code>
    <ul>
      <li>OAuthのセッションユーザとFlask_login上のユーザの一元管理/li>
      <li>ユーザ情報管理ページの操作制限</li>
      <li>Googleのユーザ情報表示</li>
      <li>一意保持のためModelsにメールアドレスのカラムの追加必須</li>
      <li>ユーザー管理にメールアドレス表示(変更不可)</li>
    </ul>
  </li>
  <li>タイトルと本文内の部分一致検索、検索<code>用語のハイライト</code></li>
  <li>
    多対多のいいね機能
    <ul>
      <li>ハートアイコンクリックアニメーション</li>
      <li>未ログインはログイン後にいいねがクリック可能</li>
      <li>トップ、管理画面、詳細に<code>いいねランキング表示</code></li>
    </ul>
  </li>
  <li>投稿日・いいねの多い順／少ない順の並び替え
      <ul>
      <li><code>曜日付</code>投稿日表示（トップ、管理画面）</li>
    </ul>
  </li>
  <li>
    ページング
    <ul>
      <li>色のカスタマイズ</li>
      <li>投稿10件以下ならページング自体を非表示</li>
    </ul>
  </li>
  <li>
    ファイルアップロード
    <ul>
      <li>トップ、管理画面、詳細、更新、ランキングにキービジュアルやサムネを表示</li>
      <li>ユーザーサムネイルの<code>選択切り替え</code></li>
    </ul>
  </li>
  <li><code>ダークモード</code>ボタン設置と画像や文字色の切り替え設定</li>
  <li>1週間自動ログイン用の<code>リメンバーチェック</code>、スイッチボタン化</li>
  <li>投稿・編集時の<code>Markdownエディタ</code>追加</li>
  <li>
    グローバルナビやフッターの固定ページ動的生成
    <ul>
      <li>全テンプレートに1つのキーのみで、タイトル・エンドポイント・画像ファイル名・テンプレート名など一律に動的管理</li>
      <li>グローバルナビの<code>カレント表示</code></li>
      <li>マークダウン内のPRE要素を<code>ハイライトや行番号</code>表示</li>
      <li>各キービジュアル画像とコンテンツ作成しグレーモードに一律管理</li>
    </ul>
  </li>
  <li>環境変数とgit除外ファイルの追加</li>
  <li>Flashの配色分け表示</li>
  <li>404ページのエラーメッセージ<code>翻訳機能</code>追加</li>
  <li>UI調整
      <ul>
        <li>記事リストフェードイン、パスワード再入力や削除機能の<code>チェックボタンフェードイン</code></li>
        <li>直前のページ・トップに戻るアニメーションスクロールボタン追加</li>
        <li><code>RWD対応</code></li>
      </ul>
  </li>
  <li>カテゴリー
    <ul>
      <li>複数カテゴリー追加(多対多)</li>
      <li>動的メニューからのカテゴリー検索</li>
      <li>ページネーション・検索・カテゴリー・投稿日・いいねの<code>変更状態の一律管理</code></li>
      <li>カテゴリー選択に同期した絞り込み<code>レコメンド表示</code></li>
    </ul>
  </li>
  <li>
    成果物生成
    <ul>
      <li><code>Figma</code>による画面レイアウトと画面遷移図の作成</li>
      <li>ERAlchemy2でER図自動生成</li>
      <li>pylint / pyreverseによるクラス図作成</li>
      <li>Flask-Diagramsで画面遷移の可視化</li>
      <li><del>△Template Visualizerでテンプレート樹形図化</del></li>
      <li><del>△FlasggerでAPI一覧を生成(or <a href="https://flask-smorest.readthedocs.io/">flask-smorest</a>)</del></li>
      <li><del>△Storybook for Jinjaによるコンポーネント可視化(Node.jsによる複雑化)</del></li>
      <li><del>△Watchdog（Flask-SocketIO）による管理画面の.pyや.htmlを変更検知&自動更新</del></li>
    </ul>
  </li>
</ul>
<!-- END_TERM -->
</details>

<hr width="800">

> [!WARNING]
> **実装中機能**：今回の課題の中で追加予定の機能。

<details>
<summary>実装中機能一覧</summary>
<ul>
  <li>CloudCode操作方法の確認</li>
  <li>管理者ログイン時のUIエフェクト
      <ul>
        <li>CLAUDE CODE PluginのFrontend Designを使用</li>
        <li>**エレクトロニックフレーム**スーパーユーザーモード発動</li>
        <li>![**ノイズボタン**](https://codepen.io/jh3y/pen/PwzeRwy)</li>
        <li>![記事一覧の**ホバー時拡大**](https://codepen.io/Adir-SL/pen/RNRyVQL)</li>
        <li>![ホバー時中の**画像を拡大**](https://codepen.io/lessthanthree/pen/LENwGyZ)</li>
        <li>![**背景波紋**](https://codepen.io/soju22/pen/myVWBGa)</li>
      </ul>
  </li>
  <li>管理者(Admin)ページ作成
    <ul>
      <li>グラフ生成[**ビルドアニメーション**](https://codepen.io/nickspiel/pen/LpepvQ)</li>
      <li>固定ページの増減(HTMX)を非同期で**リアルタイム管理**</li>
      <li>カテゴリー管理</li>
      <li>ユーザーバン(論理削除)</li>
      <li>管理者会員パスワード発行サブスクによる<a href="https://codepen.io/blacklead-studio/pen/xbwaqxE" target="_brank">**カード決済**</a></li>
    </ul>
  </li>
  <li>生成AI機能(仮案)
      <ul>
          <li>可読性・記述量など複数の観点からスコア化しグラフ生成する</li>
          <li>タイトル入力で記事の自動生成</li>
          <li>記事本文からカテゴリーの自動選択</li>
          <li>記事本文の自動英語翻訳</li>
          <li>記事本文の要約を自動生成し一覧解説に掲載</li>
          <li>NGワード内包記事判定による自動バン</li>
      </ul>
  </li>
  <li>**スワイパー**</li>
  <li>二段階認証
    <ul>
      <li>ユーザーの削除時に二段階認証ユーザーはトークンを入力</li>
      <li>メール送信</li>
    </ul>
  </li>
</。ul>
</details>

<hr width="800">

> [!CAUTION]
> **未追加機能**：時間内の対応が難しかった今後の追加予定機能

<details>
<summary>未機能一覧</summary>
<ul>
  <li>例外処理
    <ul>
      <li>エラーレベルに応じたログ生成</li>
      <li>コアエラーは管理者にメール送信</li>
    </ul>
  </li>
  <li>テスト
    <ul>
      <li><a href="https://flask-web-academy.com/article/flask-unittest/">単体</a>テスト</li>
      <li><a href="https://developer.jamstack-media.com/docs/flask/9.-%E3%83%86%E3%82%B9%E3%83%88/9.1-%E3%83%A6%E3%83%8B%E3%83%83%E3%83%88%E3%83%86%E3%82%B9%E3%83%88%E3%81%A8%E7%B5%B1%E5%90%88%E3%83%86%E3%82%B9%E3%83%88%E3%81%AE%E4%BD%9C%E6%88%90/">結合</a>テスト</li>
    </ul>
  </li>
  <li>デプロイ
      <ul>
          <li>Rendarの利用確認</li>
          <li>GitHub Actionの追加</li>
          <li>自動テストによるCI/CD</li>
      </ul>
  </li>
</ul>
</details>
