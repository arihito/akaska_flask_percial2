
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
<pre><code>
📁 Memo
├─ 📄 README.md
├─ 📄 app.py
├─ 📁 auth
│  └─ 📄 views.py
├─ 📄 config.py
├─ 📁 factories
│  └─ 📄 user_factory.py
├─ 📁 favorite
│  └─ 📄 views.py
├─ 📁 fixed
│  └─ 📄 views.py
├─ 📄 forms.py
├─ 📁 instance
│  └─ 📄 memodb.sqlite
├─ 📁 memo
│  └─ 📄 views.py
├─ 📁 migrations
├─ 📄 models.py
├─ 📁 public
│  └─ 📄 views.py
├─ 📄 seed.py
├─ 📁 static
│  ├─ 📁 css
│  │  └─ 📄 style.css
│  ├─ 📁 images
│  │  ├─ 📁 fixed
│  │  ├─ 📁 memo
│  │  ├─ 📁 nouse
│  │  └─ 📁 user
│  └─ 📁 js
│     └─ 📄 main.js
├─ 📁 templates
│  ├─ 📁 auth
│  │  ├─ 📄 _formhelpers.j2
│  │  ├─ 📄 edit.j2
│  │  ├─ 📄 login.j2
│  │  └─ 📄 register.j2
│  ├─ 📄 base.j2
│  ├─ 📁 errors
│  │  └─ 📄 404.j2
│  ├─ 📁 fixed
│  │  ├─ 📄 base.j2
│  │  ├─ 📄 ...
│  │  └─ 📄 upload.j2
│  ├─ 📁 layout
│  │  ├─ 📄 footer.j2
│  │  ├─ 📄 globalnav.j2
│  │  ├─ 📄 head.j2
│  │  ├─ 📄 mode.j2
│  │  └─ 📄 sidemenu.j2
│  ├─ 📁 memo
│  │  ├─ 📄 _formhelpers.j2
│  │  ├─ 📄 base.j2
│  │  ├─ 📄 create.j2
│  │  ├─ 📄 index.j2
│  │  └─ 📄 update.j2
│  └─ 📁 public
│     ├─ 📄 aside.j2
│     ├─ 📄 detail.j2
│     └─ 📄 index.j2
├─ 📄 tree.txt
└─ 📄 views.py
</code></pre>
</details>

<hr width="800">

> [!TIP]
> **使用ライブラリ**：アプリケーション内で追加したパッケージ群。

<details>
<summary>ライブラリ一覧</summary>
<pre><code>
Package                      Version
---------------------------- -----------
alembic                      1.18.0
aniso8601                    10.0.1
annotated-types              0.7.0
anyio                        4.12.1
attrs                        25.4.0
blinker                      1.9.0
certifi                      2026.1.4
cffi                         2.0.0
charset-normalizer           3.4.4
click                        8.3.1
colorama                     0.4.6
contourpy                    1.3.3
cryptography                 46.0.3
cssbeautifier                1.15.4
cycler                       0.12.1
distro                       1.9.0
djlint                       1.36.4
dnspython                    2.8.0
EditorConfig                 0.17.1
email-validator              1.1.3
factory_boy                  3.3.3
Faker                        40.1.2
Flask                        2.3.3
Flask-Dance                  7.1.0
Flask-DebugToolbar           0.16.0
Flask-Login                  0.6.2
Flask-Migrate                3.1.0
Flask-SQLAlchemy             2.5.1
Flask-WTF                    1.2.2
fonttools                    4.61.1
google-ai-generativelanguage 0.6.15
google-api-core              2.29.0
google-api-python-client     2.188.0
google-auth                  2.48.0
google-auth-httplib2         0.3.0
google-genai                 1.60.0
google-generativeai          0.8.6
googleapis-common-protos     1.72.0
greenlet                     3.3.0
grpcio                       1.76.0
grpcio-status                1.71.2
gunicorn                     20.1.0
h11                          0.16.0
htmlmin                      0.1.12
httpcore                     1.0.9
httplib2                     0.31.2
httpx                        0.28.1
idna                         3.11
importlib_resources          6.5.2
itsdangerous                 2.2.0
Jinja2                       3.1.6
jsbeautifier                 1.15.4
jsmin                        3.0.1
json5                        0.13.0
jsonschema                   4.26.0
jsonschema-specifications    2025.9.1
kiwisolver                   1.4.9
lesscpy                      0.15.1
Mako                         1.3.10
Markdown                     3.10.1
MarkupSafe                   3.0.3
matplotlib                   3.10.8
numpy                        2.4.1
oauthlib                     3.3.1
packaging                    26.0
pandas                       3.0.0
pathspec                     1.0.3
pillow                       12.1.0
pip                          24.2
ply                          3.11
proto-plus                   1.27.0
protobuf                     5.29.5
pyasn1                       0.6.2
pyasn1_modules               0.4.2
pycparser                    2.23
pydantic                     2.12.5
pydantic_core                2.41.5
pyOpenSSL                    25.3.0
pyparsing                    3.3.2
python-dateutil              2.9.0.post0
python-dotenv                0.19.2
pytz                         2025.2
PyYAML                       6.0.3
rcssmin                      1.2.2
referencing                  0.37.0
regex                        2025.11.3
requests                     2.32.5
requests-oauthlib            2.0.0
rpds-py                      0.30.0
rsa                          4.9.1
setuptools                   80.9.0
six                          1.17.0
sniffio                      1.3.1
SQLAlchemy                   1.4.29
tenacity                     9.1.2
tqdm                         4.67.1
typing_extensions            4.15.0
typing-inspection            0.4.2
tzdata                       2025.3
uritemplate                  4.2.0
urllib3                      2.6.3
URLObject                    3.0.0
websockets                   15.0.1
Werkzeug                     2.3.8
Wikipedia-API                0.5.8
WTForms                      3.0.1
xxhash                       3.6.0
</code></pre>
</details>

<hr width="800">

> [!NOTE]
> **要件定義**：追加済み機能要件。

<details>
<summary>実装済み機能一覧</summary>
<ul>
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
        <li>Bootstrapでトップはヘッダーナビ、管理画面は再度ナビにテンプレートを分割</li>
        <li>テーブル行クリックで詳細画面に移動し、内包ボタンとの衝突回避</li>
      </ul>
  </li>
  <li>
    ユーザログイン認証
    <ul>
      <li>未ログインのアクセス制限</li>
      <li>サインアップにメールアドレス入力フォーム追加</li>
      <li>ユーザ名は同姓同名を考慮し一意を解除し、メールアドレスを一意でログイン判定の基準に変更</li>
    </ul>
  </li>

  <li>認可（自身の投稿のみCRUD制限）</li>
  <li>タイトルと本文内の部分一致検索、検索用語のハイライト</li>
  <li>
    多対多のいいね機能
    <ul>
      <li>ハートアイコンクリックアニメーション</li>
      <li>未ログインはログイン</li>
      <li>いいねランキング</li>
      <li>トップ、管理画面、詳細にランキング表示</li>
    </ul>
  </li>
  <li>投稿日・いいねの多い順／少ない順の並び替え
      <ul>
      <li>曜日付投稿日表示（トップ、管理画面）</li>
      <li>投稿日・いいね・検索用語の状態を保持</li>
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
    </ul>
  </li>

  <li>ダークモードボタン設置と画像や文字色の切り替え設定</li>
  <li>1週間自動ログイン用のリメンバーチェック、スイッチボタン化</li>
  <li>投稿・編集時のMarkdownエディタ追加</li>
  <li>キービジュアルとロゴの調整</li>
  <li>
    グローバルナビやフッターの固定ページ17個作成
    <ul>
      <li>全テンプレートに1つのキーのみで、タイトル・エンドポイント・画像ファイル名・テンプレート名など一律に動的管理</li>
      <li>グロバルナビのカレント表示</li>
      <li>PRE要素をPrism.jsでハイライト、行番号表示</li>
      <li>各キービジュアル画像とコンテンツ作成</li>
    </ul>
  </li>
  <li>環境変数とgit除外ファイルの追加</li>
  <li>Flashの表示</li>
  <li>404ページ作成し、エラーメッセージの翻訳機能追加</li>
  <li>直前のページ・トップに戻るアニメーションスクロールボタン追加</li>
  <li>記事リストフェードイン、パスワード再入力のフェードイン</li>
  <li>ユーザの画像追加
      <ul>
      <li>モデルやフォーム、ダミーなどの変更</li>
      <li>パスワード追加任意設定</li>
      <li>画像のラジオボタン化、カレント表示</li>
      <li>削除ボタン追加</li>
    </ul>
  </li>
  <li>Google OAuth
    <ul>
      <li>OAuthのセッションユーザとFlask_login上のユーザの一元管理/li>
      <li>ユーザ情報管理ページの操作制限</li>
      <li>Googleのユーザ情報表示</li>
      <li>一意保持のためModelsにメールアドレスのカラムの追加必須</li>
      <li>ユーザー管理にメールアドレス表示(変更不可)</li>
    </ul>
  </li>
</ul>
</details>

<hr width="800">

> [!WARNING]
> **実装中機能**：今回の課題の中で追加予定の機能。

<details>
<summary>実装中機能一覧</summary>
<ul>
  <li>スマホ対応</li>
  <li>Markdownの記事本文のボリュームを増やすため1000字程度で別ファイルに10件</li>
  <li>検索と並び替えの固定記事作成(AIで基本フロー生成)</li>
  <li>カテゴリー
    <ul>
      <li>複数カテゴリー追加(多対多):basic/CRUD/UI/auth/package/APIなど</li>
      <li>カテゴリー検索</li>
    </ul>
  </li>
  <li>管理者(Admin)ページ作成
    <ul>
      <li>固定ページの増減(HTMX)で非同期管理</li>
      <li>カテゴリー管理</li>
      <li>ユーザーバン(論理削除)</li>
      <li>NGワード内包記事AI判定による自動バン</li>
      <li>管理者会員パスワード発行サブスクによるカード決済</li>
    </ul>
  </li>
  <li>投稿記事の要約文をAIによる自動生成</li>
  <li>多言語設定</li>
  <li>サイドメニュー：その他のお問い合わせによるチャットボットFAQと管理者宛てメール送信</li>
</ul>
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
  <li>
    成果物生成
    <ul>
      <li>ERAlchemy2でER図自動生成</li>
      <li>pylint / pyreverseによるクラス図作成</li>
      <li>Flask-Diagramsで画面遷移の可視化</li>
      <li>Template Visualizerでテンプレート樹形図化</li>
      <li>FlasggerでAPI一覧を生成</li>
      <li>Storybook for Jinjaによるコンポーネント可視化</li>
      <li>
        上記を管理画面上でページの自動更新化
        <ul>
          <li><strong>Watchdog</strong>（Pythonライブラリ）を使い、<code>.py</code> ファイルや <code>.html</code> ファイルの変更を監視。</li>
          <li>変更を検知したら、WebSocket（Flask-SocketIO）を通じてブラウザに「再読み込み信号」を送り図を更新。</li>
        </ul>
      </li>
      <li>
        ツール互換性判定と代替案
        <ul>
          <li><strong>ERAlchemy2　○ 可能：</strong>SQLAlchemyのmetadataを介するため、Flaskのバージョンに依存せず動作します。</li>
          <li><strong>Pyreverse　○ 可能：</strong>ソースコード（.py）を静的解析するため、実行環境のライブラリ依存関係は関係ありません。</li>
          <li>
            <strong>Flask-Diagrams　× 厳しい：</strong>
            最終更新が古く、Flask 2.3以降のRouting構造に対応していない可能性が高いです。
            ⇒ <code>app.url_map</code> をループで回して <strong>Mermaid形式の文字列</strong> を生成
          </li>
          <li><strong>Template Visualizer　△ 微妙：</strong>VS Code拡張などの静的解析ツールなら使えますが、Flask 2.3の内部構造と連携するものは注意が必要です。</li>
          <li>
            <strong>Flasgger　△ 注意：</strong>Werkzeug 2.3以上でエラーが出るケースが報告されています。
            ⇒ <a href="https://flask-smorest.readthedocs.io/">flask-smorest</a>
          </li>
          <li><strong>Storybook for Jinja　△ 難易度高：</strong>Node.js環境とのハイブリッド構成になるため、管理画面への組み込みは複雑です。</li>
        </ul>
      </li>
    </ul>
  </li>
  <li>デプロイ
      <ul>
          <li>Rendarの利用確認</li>
          <li>GitHub Actionの追加</li>
      </ul>
  </li>
</ul>
</details>
