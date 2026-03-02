# ログ可視化機能 Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 管理画面サイドメニューの「テスト網羅率状況」の直下に「ログ可視化」リンクを追加し、`/admin/logs` 専用ページで過去1日/3日/7日のアプリログを構造化テーブルで表示する。

**Architecture:** `utils/logger.py` のファイルハンドラーレベルを INFO に下げてログ量を確保。`admin/views.py` に `/admin/logs` ルートを追加しログファイルを読み込んでパース。`templates/admin/logs.j2` に Bootstrap5.3 + secondary カラーベースの構造化テーブルUIを実装。

**Tech Stack:** Flask, Bootstrap 5.3, Font Awesome 4.x, Jinja2, Python `re` モジュール（ログパース）

---

## 参照ファイル一覧

| ファイル | 目的 |
|---------|------|
| `utils/logger.py` | ロギング設定（ファイルハンドラーのレベル変更） |
| `admin/views.py` | `/admin/logs` ルート追加 |
| `templates/admin/logs.j2` | 新規テンプレート |
| `templates/admin/sidemenu.j2` | サイドバー（PC）へのリンク追加 |
| `templates/admin/sidemenu_nav.j2` | オフキャンバス（SP）へのリンク追加 |
| `static/js/main.js` | JSレベルフィルター機能追加 |
| `templates/admin/coverage.j2` | デザインの参考（トンマナ確認用） |

---

### Task 1: ログレベルを INFO に変更

**Files:**
- Modify: `utils/logger.py:29`

**Step 1: 現状確認**
```bash
grep -n "setLevel" utils/logger.py
```
期待出力: `29:    file_handler.setLevel(logging.WARNING)`

**Step 2: WARNING → INFO に変更**

`utils/logger.py` の29行目を以下に変更:
```python
    file_handler.setLevel(logging.INFO)
```

**Step 3: 動作確認**
アプリを再起動して `logs/app.log` に INFO ログが書き込まれることを確認。
```bash
FLASK_DEBUG=1 python app.py &
# ブラウザでトップページにアクセス
cat logs/app.log | head -20
```
`INFO` レベルのログが出力されていればOK（INFO行が現れる）。

**Step 4: Commit**
```bash
git add utils/logger.py
git commit -m "fix: lower log file handler level from WARNING to INFO"
```

---

### Task 2: `/admin/logs` バックエンドルート追加

**Files:**
- Modify: `admin/views.py`（末尾付近、coverage ルートの後に追加）

**Step 1: ログパース関数と logs ルートを追加**

`admin/views.py` の末尾（`})()` の前）に以下を追加。
インポートに `timedelta` が必要なので確認:

```python
# admin/views.py 先頭のインポート確認
from datetime import datetime, timezone, date, timedelta
```

`timedelta` がなければ追記する。

**Step 2: ルート実装**

`admin/views.py` の末尾に追加:

```python
# ===== ログ可視化 =====

def _parse_log_line(line):
    """1行のログを辞書にパースする。パース失敗時は None を返す。"""
    pattern = r'^\[(.+?)\] (\w+) \[(.+?)\] (.+)$'
    m = re.match(pattern, line.strip())
    if not m:
        return None
    return {
        'datetime': m.group(1),
        'level': m.group(2).upper(),
        'module': m.group(3),
        'message': m.group(4),
    }


@admin_bp.route('/logs')
@admin_required
def logs():
    days = int(request.args.get('days', 1))
    if days not in (1, 3, 7):
        days = 1

    log_path = current_app.root_path + '/logs/app.log'
    entries = []

    if os.path.exists(log_path):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        with open(log_path, encoding='utf-8') as f:
            for line in f:
                entry = _parse_log_line(line)
                if not entry:
                    continue
                # 日時パース（フォーマット: 2026-03-02 14:23:10,123）
                try:
                    dt = datetime.strptime(entry['datetime'][:19], '%Y-%m-%d %H:%M:%S')
                    dt = dt.replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
                if dt >= cutoff:
                    entries.append(entry)

    # 新しい順
    entries.reverse()

    summary = {
        'error': sum(1 for e in entries if e['level'] == 'ERROR'),
        'warning': sum(1 for e in entries if e['level'] == 'WARNING'),
        'info': sum(1 for e in entries if e['level'] == 'INFO'),
        'total': len(entries),
    }

    return render_template('admin/logs.j2', logs=entries, days=days, summary=summary)
```

**Step 3: 動作確認**

```bash
# ブラウザで http://127.0.0.1:5000/admin/logs にアクセス
# 500エラーなく表示されればOK（ログが0件でも空テーブルが表示される）
```

**Step 4: Commit**
```bash
git add admin/views.py
git commit -m "feat: add /admin/logs route for log visualization"
```

---

### Task 3: ログ可視化テンプレート作成

**Files:**
- Create: `templates/admin/logs.j2`

**デザイン仕様:**
- `coverage.j2` と同じトンマナ（Bootstrap5.3 + `btn-outline-secondary` + `#234` カラー）
- サマリーカード3列（ERROR / WARNING / INFO）
- JSレベルフィルターボタン（ALL / ERROR / WARNING / INFO）
- 構造化テーブル（日時・レベルバッジ・モジュール・メッセージ）
- レベルバッジ: ERROR=不透明、WARNING=opacity-75、INFO=opacity-50
- ERROR行は `table-secondary` クラスで強調

**Step 1: テンプレートを作成**

```jinja2
{% extends "admin/base.j2" %}
{% block page_title %}ログ可視化 | {{ SITE_NAME }}{% endblock %}

{% block content %}
<div class="py-4">

    {# ===== ヘッダー ===== #}
    <div class="d-flex align-items-center justify-content-between mb-4 fade-in fade-delay-2">
        <h2 class="mb-0"><i class="fa fa-list-alt me-2"></i>ログ可視化</h2>
        <div class="btn-group" role="group" aria-label="期間選択">
            <a href="{{ url_for('admin.logs', days=1) }}"
               class="btn btn-outline-secondary {% if days == 1 %}active{% endif %}">1日</a>
            <a href="{{ url_for('admin.logs', days=3) }}"
               class="btn btn-outline-secondary {% if days == 3 %}active{% endif %}">3日</a>
            <a href="{{ url_for('admin.logs', days=7) }}"
               class="btn btn-outline-secondary {% if days == 7 %}active{% endif %}">7日</a>
        </div>
    </div>

    {# ===== サマリーカード ===== #}
    <div class="row g-3 mb-4 fade-in fade-delay-4">
        <div class="col-4">
            <div class="card border-secondary text-center py-3 h-100">
                <div class="card-body">
                    <div class="display-4 fw-bold" style="color:#234;">{{ summary.error }}</div>
                    <p class="text-body-secondary mb-0 mt-2 border-top pt-2">
                        <span class="badge bg-secondary me-1">ERROR</span>件
                    </p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card border-secondary text-center py-3 h-100">
                <div class="card-body">
                    <div class="display-4 fw-bold text-body-secondary">{{ summary.warning }}</div>
                    <p class="text-body-secondary mb-0 mt-2 border-top pt-2">
                        <span class="badge bg-secondary opacity-75 me-1">WARNING</span>件
                    </p>
                </div>
            </div>
        </div>
        <div class="col-4">
            <div class="card border-secondary text-center py-3 h-100">
                <div class="card-body">
                    <div class="display-4 fw-bold text-body-secondary opacity-75">{{ summary.info }}</div>
                    <p class="text-body-secondary mb-0 mt-2 border-top pt-2">
                        <span class="badge bg-secondary opacity-50 me-1">INFO</span>件
                    </p>
                </div>
            </div>
        </div>
    </div>

    {# ===== レベルフィルター ===== #}
    <div class="d-flex align-items-center gap-2 mb-3 fade-in fade-delay-6">
        <small class="text-body-secondary me-1"><i class="fa fa-filter me-1"></i>フィルター:</small>
        <button class="btn btn-sm btn-outline-secondary active" id="logFilterAll">
            ALL <span class="badge bg-secondary ms-1">{{ summary.total }}</span>
        </button>
        <button class="btn btn-sm btn-outline-secondary" id="logFilterError" data-level="ERROR">
            ERROR <span class="badge bg-secondary ms-1">{{ summary.error }}</span>
        </button>
        <button class="btn btn-sm btn-outline-secondary" id="logFilterWarning" data-level="WARNING">
            WARNING <span class="badge bg-secondary ms-1">{{ summary.warning }}</span>
        </button>
        <button class="btn btn-sm btn-outline-secondary" id="logFilterInfo" data-level="INFO">
            INFO <span class="badge bg-secondary ms-1">{{ summary.info }}</span>
        </button>
    </div>

    {# ===== ログテーブル ===== #}
    {% if logs %}
    <div class="card border-secondary fade-in fade-delay-8">
        <div class="table-responsive">
            <table class="table table-sm table-hover align-middle mb-0" id="logTable">
                <thead>
                    <tr class="text-body-secondary" style="font-size:0.78rem;letter-spacing:.04em;text-transform:uppercase;">
                        <th style="width:160px;">日時</th>
                        <th style="width:90px;">レベル</th>
                        <th style="width:160px;">モジュール</th>
                        <th>メッセージ</th>
                    </tr>
                </thead>
                <tbody>
                    {% for entry in logs %}
                    <tr class="log-row {% if entry.level == 'ERROR' %}table-secondary fw-semibold{% endif %}"
                        data-level="{{ entry.level }}">
                        <td class="font-monospace" style="font-size:0.8rem;white-space:nowrap;">
                            {{ entry.datetime[:19] }}
                        </td>
                        <td>
                            {% if entry.level == 'ERROR' %}
                            <span class="badge bg-secondary">{{ entry.level }}</span>
                            {% elif entry.level == 'WARNING' %}
                            <span class="badge bg-secondary opacity-75">{{ entry.level }}</span>
                            {% else %}
                            <span class="badge bg-secondary opacity-50">{{ entry.level }}</span>
                            {% endif %}
                        </td>
                        <td class="font-monospace text-body-secondary" style="font-size:0.78rem;">
                            {{ entry.module }}
                        </td>
                        <td style="font-size:0.85rem;word-break:break-all;">
                            {{ entry.message }}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>
    {% else %}
    <div class="card border-secondary fade-in fade-delay-8">
        <div class="card-body text-center py-5">
            <i class="fa fa-inbox fa-3x text-body-secondary mb-3"></i>
            <p class="text-body-secondary mb-0">
                過去{{ days }}日間のログはありません。<br>
                アプリを操作するとログが記録されます。
            </p>
        </div>
    </div>
    {% endif %}

</div>
{% endblock %}
```

**Step 2: 動作確認**

ブラウザで `http://127.0.0.1:5000/admin/logs` を開き、テーブルが表示されることを確認。

**Step 3: Commit**
```bash
git add templates/admin/logs.j2
git commit -m "feat: add admin logs template with summary cards and level filter"
```

---

### Task 4: JSレベルフィルター追加

**Files:**
- Modify: `static/js/main.js`（末尾の `})();` の直前に追加）

**Step 1: main.jsの末尾（最後の `})();` の直前）に追加**

```javascript
/* =========================
  ログ可視化 - レベルフィルター
========================== */
const logFilterButtons = document.querySelectorAll('[id^="logFilter"]');
if (logFilterButtons.length) {
    logFilterButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // アクティブ切り替え
            logFilterButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            const level = btn.dataset.level || null; // ALL の場合は undefined
            document.querySelectorAll('#logTable .log-row').forEach(row => {
                if (!level || row.dataset.level === level) {
                    row.classList.remove('d-none');
                } else {
                    row.classList.add('d-none');
                }
            });
        });
    });
}
```

**Step 2: 動作確認**

ブラウザで ERROR / WARNING / INFO ボタンをクリックし、該当行のみ表示されることを確認。ALL で全行が戻ることを確認。

**Step 3: Commit**
```bash
git add static/js/main.js
git commit -m "feat: add log level filter JS for admin logs page"
```

---

### Task 5: サイドメニューにリンク追加

**Files:**
- Modify: `templates/admin/sidemenu.j2:43-44`
- Modify: `templates/admin/sidemenu_nav.j2:45-46`

**Step 1: sidemenu.j2 の「テスト網羅率状況」行の直後（44行目付近）に追加**

追加前（43行目）:
```html
                        <li class="nav-item fade-in fade-in-delay-11"><a class="nav-link text-body-secondary fs-5 {% if request.endpoint == 'admin.coverage' %}active{% endif %}" href="{{ url_for('admin.coverage') }}"><i class="fa fa-table me-2"></i>テスト網羅率状況</a></li>
```

追加後（43〜46行目）:
```html
                        <li class="nav-item fade-in fade-in-delay-11"><a class="nav-link text-body-secondary fs-5 {% if request.endpoint == 'admin.coverage' %}active{% endif %}" href="{{ url_for('admin.coverage') }}"><i class="fa fa-table me-2"></i>テスト網羅率状況</a></li>
                        <hr>
                        <li class="nav-item fade-in fade-in-delay-11"><a class="nav-link text-body-secondary fs-5 {% if request.endpoint == 'admin.logs' %}active{% endif %}" href="{{ url_for('admin.logs') }}"><i class="fa fa-list-alt me-2"></i>ログ可視化</a></li>
```

**Step 2: sidemenu_nav.j2 も同様に修正**

（sidemenu.j2 と同じ箇所・同じ内容を追加する）

**Step 3: 動作確認**

ブラウザでサイドメニューに「ログ可視化」リンクが表示され、クリックして遷移できることを確認。

**Step 4: Commit**
```bash
git add templates/admin/sidemenu.j2 templates/admin/sidemenu_nav.j2
git commit -m "feat: add log visualization link to admin side menu"
```

---

### Task 6: 最終動作確認

**Step 1: アプリを再起動して全体動作確認**
```bash
FLASK_DEBUG=1 python app.py
```

**Step 2: 確認項目**

- [ ] `logs/app.log` に INFO レベルのログが記録されている
- [ ] `/admin/logs` でサマリーカード（ERROR/WARNING/INFO件数）が表示される
- [ ] 期間切り替え（1日/3日/7日）でボタンがアクティブ切り替えされURLが変わる
- [ ] レベルフィルター（ALL/ERROR/WARNING/INFO）が機能する
- [ ] サイドメニュー（PC・SP両方）に「ログ可視化」リンクが表示される
- [ ] ログ0件の場合は空状態メッセージが表示される

**Step 3: 最終 Commit（未コミットがあれば）**
```bash
git add -A
git commit -m "feat: implement log visualization (#2)"
```
