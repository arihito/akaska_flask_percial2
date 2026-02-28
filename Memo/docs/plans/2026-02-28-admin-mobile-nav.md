# 管理画面モバイルナビ改善 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** スマホ表示時に管理ヘッダーが潰れる問題を解消し、三本線アイコンからオフキャンバスで全メニューにアクセスできるようにする。

**Architecture:** `base.j2` のナビバーをスマホ・PC で出し分け。スマホ時は三本線 + ポイント + サムネのみを表示し、Bootstrap Offcanvas でサイドメニュー全体とマイページ/ログアウトを提供する。PC 時（768px+）は現状維持。

**Tech Stack:** Bootstrap 5.3 Offcanvas, Jinja2 include, CSS media query

---

### Task 1: `base.j2` ナビバーのスマホ対応

**Files:**
- Modify: `templates/admin/base.j2`

**Step 1: ナビバー右側のボタン群を PC 専用に変更**

`base.j2` の 26〜31 行目、マイページリンクとログアウトボタンに `d-none d-md-flex` / `d-none d-md-block` を追加する。
ユーザー名テキスト（`<span class="user-name ...">）` は `d-none d-md-inline` にする。

変更前（26〜31行）:
```jinja2
<a class="d-flex align-items-center text-decoration-none me-3" href="{{ url_for('memo.index') }}">
    <img ... class="user-icon me-2 fade-in fade-in-delay-8 rounded-circle" ...>
    <span class="user-name fade-in fade-in-delay-16 text-body-secondary"><strong>{{ current_user.username }}</strong> さん</span>
</a>
<a class="btn btn-outline-secondary me-2 fade-in fade-in-delay-20" href="{{ url_for('memo.index') }}"><i class="fa fa-arrow-left me-1"></i>マイページ</a>
<a class="btn btn-outline-secondary fade-in fade-in-delay-20" href="{{ url_for('admin.logout') }}"><i class="fa fa-sign-out me-1"></i>管理者ログアウト</a>
```

変更後:
```jinja2
<a class="d-flex align-items-center text-decoration-none me-3" href="{{ url_for('memo.index') }}">
    <img src="{{ url_for('static', filename='images/user/' ~ current_user.thumbnail) }}" alt="{{ current_user.username }}" class="user-icon me-2 fade-in fade-in-delay-8 rounded-circle" width="" height="">
    <span class="user-name fade-in fade-in-delay-16 text-body-secondary d-none d-md-inline"><strong>{{ current_user.username }}</strong> さん</span>
</a>
<a class="btn btn-outline-secondary me-2 fade-in fade-in-delay-20 d-none d-md-block" href="{{ url_for('memo.index') }}"><i class="fa fa-arrow-left me-1"></i>マイページ</a>
<a class="btn btn-outline-secondary fade-in fade-in-delay-20 d-none d-md-block" href="{{ url_for('admin.logout') }}"><i class="fa fa-sign-out me-1"></i>管理者ログアウト</a>
```

**Step 2: ナビバー左端に三本線ボタンを追加（スマホ専用）**

`base.j2` のナビバー開始直後（ブランド名 `<a>` の前）に追加:
```jinja2
<button class="navbar-toggler border-0 d-md-none me-2" type="button"
        data-bs-toggle="offcanvas" data-bs-target="#adminOffcanvas"
        aria-controls="adminOffcanvas" aria-label="メニューを開く">
    <i class="fa fa-bars fa-lg"></i>
</button>
```

**Step 3: 動作確認（目視）**

- ブラウザで幅を 480px に縮小し、ナビバーの表示が「三本線 / 管理者専用 / ポイント / サムネ」だけになることを確認
- PC 幅（>768px）では三本線が消え、マイページ・ログアウトボタンが表示されることを確認

---

### Task 2: Offcanvas パネルを `base.j2` に追加

**Files:**
- Modify: `templates/admin/base.j2`

**Step 1: Offcanvas HTML を `{% include 'admin/sidemenu_modals.j2' %}` の直後に追加**

`base.j2` の 41 行目（`{% include 'admin/sidemenu_modals.j2' %}` の次行）に以下を挿入:

```jinja2
{# モバイル用オフキャンバスメニュー（d-md-none で PC では非表示） #}
<div class="offcanvas offcanvas-start d-md-none" tabindex="-1" id="adminOffcanvas" aria-labelledby="adminOffcanvasLabel">
    <div class="offcanvas-header border-bottom">
        <div class="d-flex align-items-center gap-2">
            <img src="{{ url_for('static', filename='images/user/' ~ current_user.thumbnail) }}"
                 alt="{{ current_user.username }}"
                 class="rounded-circle user-icon" width="36" height="36">
            <span class="fw-bold">{{ current_user.username }} さん</span>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="offcanvas" aria-label="閉じる"></button>
    </div>
    <div class="offcanvas-body p-0">
        <div class="d-flex gap-2 px-3 py-2 border-bottom">
            <a class="btn btn-outline-secondary btn-sm flex-fill text-center" href="{{ url_for('memo.index') }}">
                <i class="fa fa-arrow-left me-1"></i>マイページ
            </a>
            <a class="btn btn-outline-secondary btn-sm flex-fill text-center" href="{{ url_for('admin.logout') }}">
                <i class="fa fa-sign-out me-1"></i>ログアウト
            </a>
        </div>
        {% include 'admin/sidemenu.j2' %}
    </div>
</div>
```

**Step 2: 動作確認（目視）**

- スマホ幅で三本線をタップ → 左からメニューがスライドイン
- ヘッダーにユーザー名・マイページ・ログアウトが表示される
- サイドメニュー項目（ダッシュボード、固定ページ管理、等）が全て表示される
- 各リンクをタップして遷移できる（オフキャンバスが自動で閉じる）

---

### Task 3: オフキャンバスの背景スタイルを `style.css` に追加

**Files:**
- Modify: `static/css/style.css`

**Step 1: `/* 管理画面 */` セクション末尾付近にオフキャンバス用スタイルを追加**

`style.css` の管理画面セクション（`/* 管理サイドバー 閃光エフェクト */` ブロックの後）に追加:

```css
/* モバイル用オフキャンバスメニュー */
#adminOffcanvas .offcanvas-body {
    background: linear-gradient(to top, rgb(43 48 53), #343A40);
}
#adminOffcanvas .offcanvas-header {
    background: #343A40;
    color: #ccc;
}
[data-bs-theme="light"] #adminOffcanvas .offcanvas-body {
    background: linear-gradient(to top, #dedadc, #fefafe);
}
[data-bs-theme="light"] #adminOffcanvas .offcanvas-header {
    background: #fefafe;
}
```

**Step 2: 動作確認（ダークモード・ライトモード両方）**

- ダークモードでオフキャンバスを開き、サイドバーと同じダーク背景になっていることを確認
- ライトモードに切り替えて同様に確認

---

### Task 4: 最終動作確認 & コミット

**Step 1: スマホ幅で全ページを動作確認**

以下の管理画面ページをスマホ幅（480px）で確認:
- `/admin/` ダッシュボード
- `/admin/fixed` 固定ページ管理
- `/admin/category` カテゴリー管理

確認項目:
- ナビバーが潰れていない
- 三本線タップでオフキャンバスが開く
- 全メニューリンクが機能する
- マイページ・ログアウトが機能する

**Step 2: PC 幅で既存レイアウトに影響がないことを確認**

- サイドバーが左に表示される
- ナビバーにマイページ・ログアウトボタンが表示される
- 三本線ボタンが見えない

**Step 3: コミット（`Percial2/` 階層から実行）**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/templates/admin/base.j2 Memo/static/css/style.css
git commit -m "feat: admin mobile nav - offcanvas side menu for smartphones"
```
