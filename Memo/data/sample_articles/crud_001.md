# Flask-SQLAlchemyによるCRUD操作の実装

## SQLAlchemyの基本概念

Flask-SQLAlchemyは、PythonのORM（Object-Relational Mapping）ライブラリであるSQLAlchemyをFlaskで使いやすくしたものです。データベース操作をPythonオブジェクトとして扱えます。

## モデル定義

```python
# models.py
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Article(db.Model):
    __tablename__ = 'articles'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Article {self.title}>'
```

## Create（作成）

新しいレコードを作成する際は、モデルのインスタンスを生成してセッションに追加します。

```python
@app.route('/article/create', methods=['POST'])
def create_article():
    article = Article(
        title=request.form['title'],
        content=request.form['content']
    )
    db.session.add(article)
    db.session.commit()
    flash('記事を作成しました')
    return redirect(url_for('index'))
```

## Read（読み取り）

データの取得にはクエリメソッドを使用します。

### 全件取得
```python
articles = Article.query.all()
```

### 条件付き取得
```python
article = Article.query.filter_by(id=1).first()
# または
article = Article.query.get(1)
```

### ページネーション
```python
page = request.args.get('page', 1, type=int)
articles = Article.query.paginate(page=page, per_page=10)
```

## Update（更新）

既存のレコードを更新する場合は、オブジェクトの属性を変更してコミットします。

```python
@app.route('/article/<int:id>/update', methods=['POST'])
def update_article(id):
    article = Article.query.get_or_404(id)
    article.title = request.form['title']
    article.content = request.form['content']
    db.session.commit()
    flash('記事を更新しました')
    return redirect(url_for('show_article', id=id))
```

## Delete（削除）

レコードの削除には`delete()`メソッドを使用します。

```python
@app.route('/article/<int:id>/delete', methods=['POST'])
def delete_article(id):
    article = Article.query.get_or_404(id)
    db.session.delete(article)
    db.session.commit()
    flash('記事を削除しました')
    return redirect(url_for('index'))
```

## トランザクション管理

SQLAlchemyではセッション単位でトランザクションが管理されます。

```python
try:
    article = Article(title='タイトル', content='内容')
    db.session.add(article)
    db.session.commit()
except Exception as e:
    db.session.rollback()
    flash('エラーが発生しました')
```

## リレーションシップの扱い

1対多のリレーションシップを定義する例：

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    articles = db.relationship('Article', backref='author')

class Article(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
```

## まとめ

Flask-SQLAlchemyを使うことで、SQL文を直接書くことなくデータベース操作が可能になります。セッション管理とトランザクション処理を適切に行うことで、データの整合性を保ちながら安全にCRUD操作を実装できます。

## バルク操作でパフォーマンスを向上させる

大量データを個別にINSERTするとパフォーマンスが低下します。SQLAlchemyのバルク操作を活用しましょう。

```python
# バルクINSERT（推奨）
from sqlalchemy import insert

db.session.execute(
    insert(Article),
    [{'title': f'記事{i}', 'content': f'内容{i}', 'user_id': 1} for i in range(1000)]
)
db.session.commit()
```

SQLAlchemy 2.0では `session.execute(insert(...))` 形式が推奨されており、従来の `bulk_insert_mappings` より効率的です。1000件のINSERTでも1回のトランザクションで完了するため、ループで1件ずつ追加するより大幅に高速です。

## トランザクション管理の実践

複数テーブルへの書き込みが絡む処理では、トランザクションの扱いを明示的に意識します。

```python
def transfer_article(article_id, new_user_id):
    try:
        article = db.session.get(Article, article_id)
        article.user_id = new_user_id
        db.session.add(ActivityLog(action='transfer', article_id=article_id))
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        raise e
```

`try / except` でロールバックを明示することで、部分的な書き込みによるデータ不整合を防ぎます。`with db.session.begin():` を使うコンテキストマネージャ形式では自動コミット・ロールバックが行われます。

## クエリの最適化

N+1問題はFlaskアプリのパフォーマンスボトルネックになりやすい問題です。`joinedload` や `selectinload` で対策します。

```python
from sqlalchemy.orm import joinedload, selectinload

# N+1問題が発生するクエリ（悪い例）
articles = Article.query.all()
for article in articles:
    print(article.author.username)  # ← 記事ごとにSQLが発行される

# joinedload で解決（良い例）
articles = Article.query.options(joinedload(Article.author)).all()
for article in articles:
    print(article.author.username)  # ← JOINで一括取得済み
```

`SQLALCHEMY_ECHO = True` を設定すると発行されるSQLがコンソールに出力されるため、N+1問題の検出に役立ちます。
