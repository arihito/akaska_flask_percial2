# English Public Pages Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 翻訳済み記事を `/en/` URLで公開し、Googleが英語ページとして検索インデックスできるようにする。

**Architecture:** `public_bp` に `/en/` と `/en/detail/<id>` ルートを追加し、既存テンプレートに `is_english` フラグを渡すことで表示を切り替える。`app.py` の `context_processor` で `is_english` と `lang_switch_url` を全テンプレートに自動注入。`head.j2` に hreflang タグを追加しSEO対応。

**Tech Stack:** Flask Blueprint, Jinja2, Bootstrap5.3, SQLAlchemy (ai_score JSON カラム)

---

## 変更ファイル一覧

| ファイル | 変更内容 |
|----------|---------|
| `app.py` | `is_english` / `lang_switch_url` / `EN_LABELS` を context_processor に追加 |
| `templates/layout/head.j2` | `lang` 属性を動的化・hreflang タグ追加 |
| `templates/layout/globalnav.j2` | 言語切替ボタン追加 |
| `templates/layout/footer.j2` | 英語UI文言対応 |
| `public/views.py` | `/en/` と `/en/detail/<id>` ルート追加 |
| `templates/public/index.j2` | `is_english` フラグで翻訳タイトル/要約に切替 |
| `templates/public/detail.j2` | `is_english` フラグで翻訳本文に切替 |

---

### Task 1: context_processor に英語判定を追加（`app.py`）

**Files:**
- Modify: `app.py:79-92`

**Step 1: `inject_static_pages` に英語判定ロジックを追記**

`app.py` の `inject_static_pages` context_processor を以下に置き換える：

```python
@app.context_processor
def inject_static_pages():
    from flask import request as _req
    try:
        pages = FixedPage.query.filter_by(visible=True).order_by(FixedPage.order).all()
        GLOBAL_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'global'}
        FOOTER_NAV_PAGES = {p.key: p.title for p in pages if p.nav_type == 'footer'}
    except Exception:
        GLOBAL_NAV_PAGES = {}
        FOOTER_NAV_PAGES = {}

    # 英語ページ判定
    is_english = _req.path.startswith('/en')

    # 言語切替URL（/en/detail/1 → /detail/1、/detail/1 → /en/detail/1）
    path = _req.path
    if path.startswith('/en'):
        lang_switch_url = path[3:] or '/'
    else:
        lang_switch_url = '/en' + path

    # 英語UI文言辞書
    EN_LABELS = {
        'login': 'Sign In',
        'register': 'Register',
        'logout': 'Sign Out',
        'top': 'Top',
        'today_pick': "Today's Pick",
        'today_pick_sub': 'Article changes randomly once a day',
        'recommended': 'Recommended for You',
        'recommended_sub': 'Articles recommended based on your post categories',
        'posted_by': 'Posted by:',
        'posted_on': 'Posted on:',
        'likes': 'Likes',
        'back_to_top': 'Back to Top',
        'back_prev': 'Previous Page',
        'back_list': 'Back to List',
        'login_prompt': 'Sign in to like!',
        'own_article': 'Your article',
        'footer_desc': (
            'This Flask tech blog was created for the purpose of learning Flask '
            'application development as a vocational training assignment.'
        ),
    }

    return dict(
        GLOBAL_NAV_PAGES=GLOBAL_NAV_PAGES,
        FOOTER_NAV_PAGES=FOOTER_NAV_PAGES,
        SITE_NAME=app.config['SITE_NAME'],
        is_english=is_english,
        lang_switch_url=lang_switch_url,
        EN_LABELS=EN_LABELS,
    )
```

**Step 2: ブラウザで `/` にアクセスして動作確認（エラーが出ないこと）**

**Step 3: コミット**

```bash
git add app.py
git commit -m "feat: add is_english/lang_switch_url/EN_LABELS to context_processor"
```

---

### Task 2: `head.j2` の lang 属性動的化 + hreflang タグ追加

**Files:**
- Modify: `templates/layout/head.j2`

**Step 1: `<html lang="ja">` を動的化し hreflang を追加**

`head.j2` を以下に変更する：

```html
<!DOCTYPE html>
<html lang="{{ 'en' if is_english else 'ja' }}">
      <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{% block page_title %}{{ SITE_NAME }}{% endblock %}</title>
            <link rel="icon" type="image/x-icon" href="{{ url_for('static', filename='favicon.ico') }}">
            <meta name="description" content="">
            <meta name="keywords" content="">
            {# hreflang: 日英ページを相互リンク（トップと詳細ページのみ） #}
            {% if request.path == '/' or request.path == '/en/' %}
                <link rel="alternate" hreflang="ja" href="{{ request.host_url.rstrip('/') }}/">
                <link rel="alternate" hreflang="en" href="{{ request.host_url.rstrip('/') }}/en/">
            {% elif request.path.startswith('/detail/') or request.path.startswith('/en/detail/') %}
                {% set detail_id = request.path.split('/')[-1] %}
                <link rel="alternate" hreflang="ja" href="{{ request.host_url.rstrip('/') }}/detail/{{ detail_id }}">
                <link rel="alternate" hreflang="en" href="{{ request.host_url.rstrip('/') }}/en/detail/{{ detail_id }}">
            {% endif %}
            <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/font-awesome/4.7.0/css/font-awesome.min.css">
            <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css">
            <link rel="stylesheet" href=" https://cdn.jsdelivr.net/npm/pretty-checkbox@3.0/dist/pretty-checkbox.min.css">
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github-dark.min.css">
            <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
            <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.7/dist/chart.umd.min.js"></script>
            <script src="https://cdn.jsdelivr.net/npm/sortablejs@1.15.3/Sortable.min.js"></script>
      </head>
      <body>
            {% block body %}
            {% endblock body %}
      </body>
</html>
```

**Step 2: `/` と `/en/` でソースを確認し、lang属性とhreflangが切り替わること**

**Step 3: コミット**

```bash
git add templates/layout/head.j2
git commit -m "feat: dynamic lang attribute and hreflang tags for EN/JA pages"
```

---

### Task 3: `/en/` と `/en/detail/<id>` ルートを追加（`public/views.py`）

**Files:**
- Modify: `public/views.py`

**Step 1: ファイル末尾に2つのルートを追加**

```python
@public_bp.route('/en/')
def public_index_en():
    """英語版トップページ（is_english=True はcontext_processorで自動付与）"""
    # 日本語版と同じロジック。テンプレート側で is_english フラグにより表示切替。
    page = request.args.get('page', 1, type=int)
    pagination = db.session.query(Memo, func.count(Favorite.id).label('like_count')).outerjoin(Favorite, Memo.id == Favorite.memo_id).group_by(Memo.id).order_by(Memo.created_at.desc()).paginate(page=page, per_page=PER_PAGE)
    raw_memos = pagination.items
    total_pages = pagination.pages
    today_seed = date.today().isoformat()
    random.seed(today_seed)
    memos = [{"memo": memo, "like_count": like_count} for memo, like_count in raw_memos]
    favorite_memo_ids = []
    if current_user.is_authenticated:
        favorite_memo_ids = [f.memo_id for f in Favorite.query.filter_by(user_id=current_user.id)]
    raw_top10 = db.session.query(Memo, func.count(Favorite.id).label("like_count")).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [{"memo": memo, "like_count": like_count} for memo, like_count in raw_top10]
    rand1 = random.choice(memos) if memos else None
    recommended = []
    if current_user.is_authenticated:
        my_memos = Memo.query.filter_by(user_id=current_user.id).all()
        if my_memos:
            my_category_ids = {category.id for memo in my_memos for category in memo.categories}
            if my_category_ids:
                other_memos = Memo.query.filter(Memo.user_id != current_user.id).all()
                scored = []
                for memo in other_memos:
                    match_count = len(my_category_ids & {c.id for c in memo.categories})
                    if match_count > 0:
                        scored.append((memo, match_count))
                scored.sort(key=lambda x: x[1], reverse=True)
                recommended = [m for m, _ in scored[:3]]
    return render_template('public/index.j2',
        memos=memos, page=page, total_pages=total_pages,
        favorite_memo_ids=favorite_memo_ids, top10=top10,
        rand1=rand1, recommended=recommended
    )


@public_bp.route('/en/detail/<int:memo_id>')
def detail_en(memo_id):
    """英語版記事詳細ページ"""
    memo = Memo.query.get_or_404(memo_id)
    memo.view_count = (memo.view_count or 0) + 1
    db.session.commit()
    like_count = Favorite.query.filter_by(memo_id=memo_id).count()
    raw_top10 = db.session.query(Memo, func.count(Favorite.id).label("like_count")).outerjoin(Favorite).group_by(Memo.id).order_by(func.count(Favorite.id).desc()).limit(10).all()
    top10 = [{"memo": memo, "like_count": like_count} for memo, like_count in raw_top10]
    return render_template('public/detail.j2', memo=memo, top10=top10, like_count=like_count)
```

**Step 2: `/en/` にアクセスしてページが表示されること確認**

**Step 3: コミット**

```bash
git add public/views.py
git commit -m "feat: add /en/ and /en/detail/<id> routes to public_bp"
```

---

### Task 4: `globalnav.j2` に言語切替ボタンを追加

**Files:**
- Modify: `templates/layout/globalnav.j2`

**Step 1: ナビ右端に言語切替ボタンを追加**

`globalnav.j2` の `</header>` の直前（ログイン/未ログインブロックの後）に追加する。
具体的には `<div class="btn-group ...">` を含む col の末尾、または別の col として追加。

未ログイン時の `<div class="col-12 col-md-6">` を以下に変更：

```html
<!-- 右側（未ログイン） -->
{% if not current_user.is_authenticated %}
  <div class="col-12 col-md-6">
      <div class="btn-group d-flex justify-content-center justify-content-md-end gap-2">
          <a class="btn btn-outline-secondary flex-fill flex-md-grow-0 fade-in fade-in-delay-16 {% if request.endpoint == 'auth.login' %}active{% endif %}" href="{{ url_for('auth.login') }}"><i class="fa fa-sign-in"></i> {{ EN_LABELS.login if is_english else 'ログイン' }}</a>
          <a class="btn btn-outline-secondary flex-fill flex-md-grow-0 fade-in fade-in-delay-20 {% if request.endpoint == 'auth.register' %}active{% endif %}" href="{{ url_for('auth.register') }}"><i class="fa fa-user-plus"></i> {{ EN_LABELS.register if is_english else '新規登録' }}</a>
          <a class="btn btn-outline-secondary flex-fill flex-md-grow-0 fade-in fade-in-delay-24" href="{{ lang_switch_url }}" title="{{ 'Switch to Japanese' if is_english else 'Switch to English' }}">{{ '🇯🇵 JP' if is_english else '🇬🇧 EN' }}</a>
      </div>
  </div>
<!-- 右側（ログイン済） -->
{% else %}
  <div class="col-12 col-md-6">
      <div class="d-flex align-items-center justify-content-center justify-content-md-end gap-3">
          <a class="text-body-secondary link-opacity-50-hover d-flex align-items-center" href="{{ url_for('memo.index') }}">
              <img src="{{ url_for('static', filename='images/user/' ~ current_user.thumbnail) }}" alt="{{ current_user.username }}" class="user-icon me-2 fade-in fade-in-delay-8 rounded-circle" width="32" height="32">
              <strong class="fade-in fade-in-delay-16">{{ current_user.username }} {% if not is_english %}さん{% endif %}</strong></a>
          <a class="btn btn-outline-secondary fade-in fade-in-delay-20" href="{{ url_for('auth.logout') }}"><i class="fa fa-sign-out"></i> {{ EN_LABELS.logout if is_english else 'ログアウト' }}</a>
          <a class="btn btn-outline-secondary fade-in fade-in-delay-24" href="{{ lang_switch_url }}" title="{{ 'Switch to Japanese' if is_english else 'Switch to English' }}">{{ '🇯🇵 JP' if is_english else '🇬🇧 EN' }}</a>
      </div>
  </div>
{% endif %}
```

また、ナビの「トップ」リンクも英語対応：

```html
<a class="nav-link link-body-emphasis px-3 ..." href="{{ url_for('public.public_index') }}">
    <i class="fa fa-home"></i> {{ EN_LABELS.top if is_english else 'トップ' }}
</a>
```

**Step 2: `/` と `/en/` でナビの文言・ボタンが切り替わること確認**

**Step 3: コミット**

```bash
git add templates/layout/globalnav.j2
git commit -m "feat: add language switcher button and EN labels to globalnav"
```

---

### Task 5: `public/index.j2` を英語表示対応

**Files:**
- Modify: `templates/public/index.j2`

**Step 1: タイトル・サマリーを `is_english` で切替**

変更箇所は以下の3か所：

**① オススメ記事のタイトル部分（line 23）：**
```html
{# 変更前 #}
<h2 class="..."><a ...>{{ rand1.memo.title }}</a></h2>

{# 変更後 #}
<h2 class="..."><a ...>
    {{ (rand1.memo.ai_score.translated_title if rand1.memo.ai_score and rand1.memo.ai_score.translated_title else rand1.memo.title) if is_english else rand1.memo.title }}
</a></h2>
```

**② オススメ記事のサマリー（line 27）：**
```html
{# 変更前 #}
<p class="card-text">{{ rand1.memo.summary if rand1.memo.summary else (rand1.memo.content | truncate(190, False, '...')) }}</p>

{# 変更後 #}
<p class="card-text">
{% if is_english and rand1.memo.ai_score and rand1.memo.ai_score.translated_body %}
    {{ rand1.memo.ai_score.translated_body | truncate(190, False, '...') }}
{% else %}
    {{ rand1.memo.summary if rand1.memo.summary else (rand1.memo.content | truncate(190, False, '...')) }}
{% endif %}
</p>
```

**③ 記事カード一覧のタイトル（line 56）：**
```html
{# 変更前 #}
<h3 class="mb-0"><a ...>{{ memo.title }}</a></h3>

{# 変更後 #}
<h3 class="mb-0"><a ...>
    {{ (memo.ai_score.translated_title if memo.ai_score and memo.ai_score.translated_title else memo.title) if is_english else memo.title }}
</a></h3>
```

**④ 記事カード一覧のサマリー（line 78）：**
```html
{# 変更前 #}
<p class="card-text mb-auto">{{ memo.summary if memo.summary else (memo.content | truncate(90, False, '...')) }}</p>

{# 変更後 #}
<p class="card-text mb-auto">
{% if is_english and memo.ai_score and memo.ai_score.translated_body %}
    {{ memo.ai_score.translated_body | truncate(90, False, '...') }}
{% else %}
    {{ memo.summary if memo.summary else (memo.content | truncate(90, False, '...')) }}
{% endif %}
</p>
```

**⑤ 見出し文言（line 12, 113）を EN_LABELS で切替：**
```html
{# line 12 変更後 #}
<i class="fa fa-calendar-o me-2"></i>{{ EN_LABELS.today_pick if is_english else '本日のオススメ記事' }}<span ...>{{ EN_LABELS.today_pick_sub if is_english else '1日1回ランダムに記事が入れ替わります' }}</span>

{# line 113 変更後 #}
<h4 ...><i class="fa fa-share-alt me-2"></i>{{ EN_LABELS.recommended if is_english else 'あなたの興味の近いオススメ記事' }}<span ...>{{ EN_LABELS.recommended_sub if is_english else 'あなたの投稿記事に付与したカテゴリーから...' }}</span></h4>
```

**⑥ ページネーションのリンク先を `/en/` に対応：**

```html
{# 変更前 #}
href="?page={{ page - 1 }}"

{# 変更後（全3箇所） #}
href="?page={{ page - 1 }}"  {# クエリパラメーターのみなので変更不要 #}
```

ページネーションはクエリパラメーター `?page=N` のみなので変更不要。

**⑦ 詳細リンクを英語URLに対応（全4箇所）：**

```html
{# 変更前 #}
href="{{ url_for('public.detail', memo_id=rand1.memo.id) }}"

{# 変更後 #}
href="{{ url_for('public.detail_en' if is_english else 'public.detail', memo_id=rand1.memo.id) }}"
```

これをファイル内の `url_for('public.detail', ...)` 全箇所に適用。

**Step 2: `/en/` で翻訳済み記事のタイトルが英語で表示されること確認**

**Step 3: コミット**

```bash
git add templates/public/index.j2
git commit -m "feat: show translated title/summary on /en/ index page"
```

---

### Task 6: `public/detail.j2` を英語表示対応

**Files:**
- Modify: `templates/public/detail.j2`

**Step 1: タイトル・本文・UI文言を切替**

```html
{% extends "base.j2" %}
{% block page_title %}
    {{ (memo.ai_score.translated_title if memo.ai_score and memo.ai_score.translated_title else memo.title) if is_english else memo.title }} | {{ SITE_NAME }}
{% endblock %}
{% block content %}
<style>
    .article-img {
        height: 300px;
        background-image: url("{{ url_for('static', filename='images/memo/' ~  (memo.image_filename if memo.image_filename else 'nofile.jpg')) }}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        filter: grayscale(100%);
    }
</style>
    <div class="mb-4 rounded text-body-emphasis bg-body-secondary article-img"></div>
    <div class="row">
        <div class="col-md-9 public">
            <h1 class="display-4 my-3 pb-4 border-bottom">
                {{ (memo.ai_score.translated_title if memo.ai_score and memo.ai_score.translated_title else memo.title) if is_english else memo.title }}
            </h1>
            <p>
                <i class="fa fa-user"></i>{{ EN_LABELS.posted_by if is_english else '投稿者:' }} {{ memo.user.username }}
                <span class="px-2">|</span>
                <i class="fa fa-calendar"></i>{{ EN_LABELS.posted_on if is_english else '投稿日時:' }} {{ memo.created_at.strftime("%Y-%m-%d %H:%M") }}
                <span class="px-2">|</span>
                ❤️ {{ like_count }} {{ EN_LABELS.likes if is_english else 'いいね' }}
            </p>
            <p class="markdown-body">
                {% if is_english and memo.ai_score and memo.ai_score.translated_body %}
                    {{ memo.ai_score.translated_body | markdown | safe }}
                {% else %}
                    {{ memo.content | markdown | safe }}
                {% endif %}
            </p>
            <nav class="navbar bg-body-secondary my-5 rounded-3">
                <div class="container-fluid d-none d-md-flex justify-content-start my-2 mx-2">
                    <a class="btn btn-secondary btn-lg text-dark flex-fill fade-in fade-delay-4 me-md-2" data-action="scrollTop"><i class="fa fa-arrow-up"></i> {{ EN_LABELS.back_to_top if is_english else 'ページの最上部に戻る' }}</a>
                    <a class="btn btn-outline-secondary btn-lg fade-in fade-delay-8 me-md-2" href="#" data-action="back"><i class="fa fa-arrow-left"></i> {{ EN_LABELS.back_prev if is_english else '直前のページに戻る' }}</a>
                    <a class="btn btn-outline-secondary btn-lg fade-in fade-delay-12" href="{{ url_for('public.public_index_en' if is_english else 'public.public_index') }}"><i class="fa fa-reply"></i> {{ EN_LABELS.back_list if is_english else 'トップの一覧に戻る' }}</a>
                </div>
                <div class="container-fluid d-md-none d-flex justify-content-start my-2 mx-2">
                    <a class="btn btn-secondary btn-lg text-dark flex-fill fade-in fade-delay-4" data-action="scrollTop"><i class="fa fa-arrow-up"></i> {{ EN_LABELS.back_to_top if is_english else 'ページの最上部に戻る' }}</a>
                    <a class="btn btn-outline-secondary btn-lg fade-in fade-delay-8 mt-2 w-100 d-block" href="#" data-action="back"><i class="fa fa-arrow-left"></i> {{ EN_LABELS.back_prev if is_english else '直前のページに戻る' }}</a>
                    <a class="btn btn-outline-secondary btn-lg fade-in fade-delay-12 mt-2 w-100 d-block" href="{{ url_for('public.public_index_en' if is_english else 'public.public_index') }}"><i class="fa fa-reply"></i> {{ EN_LABELS.back_list if is_english else 'トップの一覧に戻る' }}</a>
                </div>
            </nav>
        </div>
        {% include "public/aside.j2" %}
    </div>
{% endblock %}
```

**Step 2: `/en/detail/<翻訳済み記事のid>` で英語本文が表示されること確認**

**Step 3: コミット**

```bash
git add templates/public/detail.j2
git commit -m "feat: show translated title/body on /en/detail page"
```

---

### Task 7: `footer.j2` の英語UI文言対応

**Files:**
- Modify: `templates/layout/footer.j2`

**Step 1: フッター説明文を `is_english` で切替**

`footer.j2` の説明文段落（line 12-15）を以下に変更：

```html
<p class="col-12 col-md-10 fade-in fade-delay-5">
{% if is_english %}
    {{ EN_LABELS.footer_desc }}
{% else %}
    このFlask tech blogは、職業訓練校の課題として、Flaskアプリケーションの開発学習を目的に作成しています。<br>
    投稿記事のダミーテキストの一部は、AIによって生成しています。また、記事内容の正誤については、あくまで自身の理解をまとめたものですので、
    参考程度にご覧いただけますと幸いです。
{% endif %}
</p>
```

**Step 2: `/en/` でフッターが英語表示になること確認**

**Step 3: 最終コミット**

```bash
git add templates/layout/footer.j2
git commit -m "feat: English footer description on /en/ pages"
```

---

## 動作確認チェックリスト

- [ ] `/en/` にアクセス → `<html lang="en">` になっている
- [ ] `/en/` で翻訳済み記事のタイトルが英語表示
- [ ] `/` → 🇬🇧 EN ボタンで `/en/` に遷移
- [ ] `/en/` → 🇯🇵 JP ボタンで `/` に遷移
- [ ] `/en/detail/<id>` で翻訳済み記事の本文が英語表示
- [ ] `/en/detail/<id>` → `/detail/<id>` に言語切替できる
- [ ] ソースの `<link rel="alternate" hreflang>` が正しく出力されている
- [ ] 未翻訳記事は日本語のまま `/en/` でも表示されている
- [ ] フッターが英語ページで英語表示になっている
