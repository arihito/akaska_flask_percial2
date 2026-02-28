# テスト網羅率ページ 実装計画

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 管理画面にテストカバレッジ確認ページを追加し、任意のボタンで最新データに更新できるようにする。

**Architecture:** `GET /admin/coverage` は既存の `coverage.json` を読み込んで即時表示。`POST /admin/coverage/run` は `subprocess` で pytest を実行して `coverage.json` を生成し JSON で返す。フロントは AJAX でボタン実行・スピナー表示・DOM更新。

**Tech Stack:** Flask / Jinja2 / Bootstrap 5.3 / subprocess / coverage.py (既存) / Vanilla JS AJAX

---

## 前提

- 作業ディレクトリ: `C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo/`
- Gitルート: `C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/`
- Python環境: `C:/Users/arihi/miniconda3/envs/flask2_env/python.exe`
- `admin/views.py` は現在 1265 行。末尾に追記する。
- `static/js/main.js` は現在 1296 行。末尾（最後の `})();` の直前）に追記する。
- サイドメニューの17行目に `href=""` のプレースホルダーが既に存在する。

---

### Task 1: admin/views.py に coverage ルートを追加する

**Files:**
- Modify: `admin/views.py`（末尾に追記）

**Step 1: `admin/views.py` の末尾（1265行の後）に以下を追記する（Edit ツール）**

追記する対象（`old_string` に最終行を含める）:

```python
    return render_template(
        "mail/admin_approve.j2",
        user=current_user,
        payment_url=payment_url
    )
```

上記の後に以下を追加:

```python
    return render_template(
        "mail/admin_approve.j2",
        user=current_user,
        payment_url=payment_url
    )


# ===================================================
# テスト網羅率ページ
# ===================================================

def _parse_coverage_json(coverage_json_path):
    """coverage.json を読み込んでテンプレート用データに変換する。"""
    import json as _json
    from datetime import datetime
    if not coverage_json_path.exists():
        return None
    with open(coverage_json_path, encoding='utf-8') as f:
        data = _json.load(f)

    # 除外するファイルパターン（ノイズになるファイル）
    EXCLUDE_PATTERNS = ['__init__', 'seed.py', 'dev_print.py', 'factories/']

    totals = data['totals']
    files = []
    for name, info in sorted(data['files'].items(), key=lambda x: x[0]):
        if any(p in name for p in EXCLUDE_PATTERNS):
            continue
        pct = info['summary']['percent_covered_display']
        stmts = info['summary']['num_statements']
        covered = info['summary']['covered_lines']
        missing = info['summary']['missing_lines']
        files.append({
            'name': name.replace('\\', '/'),
            'pct': int(pct),
            'stmts': stmts,
            'covered': covered,
            'missing': missing,
        })

    mtime = coverage_json_path.stat().st_mtime
    last_run = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

    return {
        'total_pct': int(totals['percent_covered_display']),
        'total_stmts': totals['num_statements'],
        'total_covered': totals['covered_lines'],
        'total_missing': totals['missing_lines'],
        'files': files,
        'last_run': last_run,
    }


@admin_bp.route('/coverage')
@login_required
def coverage():
    coverage_json_path = Path(current_app.root_path) / 'coverage.json'
    coverage_data = _parse_coverage_json(coverage_json_path)
    return render_template('admin/coverage.j2', coverage=coverage_data)


@admin_bp.route('/coverage/run', methods=['POST'])
@login_required
def coverage_run():
    """pytest を実行して coverage.json を生成し、結果を JSON で返す。"""
    import subprocess, sys
    python = sys.executable
    project_root = Path(current_app.root_path)
    try:
        result = subprocess.run(
            [python, '-m', 'pytest', '--cov=.', '--cov-report=json', '-q', '--tb=no'],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=120,
        )
        coverage_json_path = project_root / 'coverage.json'
        coverage_data = _parse_coverage_json(coverage_json_path)
        if coverage_data is None:
            return {'ok': False, 'error': 'coverage.json が生成されませんでした'}, 500
        passed = result.returncode == 0
        return {
            'ok': True,
            'passed': passed,
            'coverage': coverage_data,
        }
    except subprocess.TimeoutExpired:
        return {'ok': False, 'error': 'タイムアウト（120秒）'}, 500
    except Exception as e:
        return {'ok': False, 'error': str(e)}, 500
```

**Step 2: Python 構文チェック**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo && "C:/Users/arihi/miniconda3/envs/flask2_env/python.exe" -c "from admin.views import admin_bp; print('OK')"
```
期待: `OK`

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2 && git add Memo/admin/views.py && git commit -m "feat: add coverage route to admin views"
```

---

### Task 2: templates/admin/coverage.j2 を作成する

**Files:**
- Create: `templates/admin/coverage.j2`

**Step 1: ファイルを作成する（Write ツール）**

`C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo/templates/admin/coverage.j2` を作成:

```jinja
{% extends "admin/base.j2" %}
{% block page_title %}テスト網羅率 | {{ SITE_NAME }}{% endblock %}

{% block content %}
<div class="py-4">

    {# ===== ヘッダー ===== #}
    <div class="d-flex align-items-center justify-content-between mb-4 fade-in">
        <h2 class="mb-0"><i class="fa fa-check-square-o me-2"></i>テスト網羅率状況</h2>
        <button id="coverageRunBtn" class="btn btn-outline-secondary btn-lg">
            <i class="fa fa-play me-1"></i>テスト実行
        </button>
    </div>

    {# ===== ローディング ===== #}
    <div id="coverageLoading" class="text-center py-5 d-none">
        <div class="spinner-border text-secondary" role="status" style="width:3rem;height:3rem;"></div>
        <p class="mt-3 text-body-secondary">pytest を実行中です。しばらくお待ちください…</p>
    </div>

    {# ===== 未実行メッセージ ===== #}
    <div id="coverageEmpty" class="{% if coverage %}d-none{% endif %}">
        <div class="card border-secondary fade-in">
            <div class="card-body text-center py-5">
                <i class="fa fa-inbox fa-3x text-body-secondary mb-3"></i>
                <p class="text-body-secondary mb-0">まだテストが実行されていません。<br>「テスト実行」ボタンを押して最新データを取得してください。</p>
            </div>
        </div>
    </div>

    {# ===== 結果パネル ===== #}
    <div id="coverageResult" class="{% if not coverage %}d-none{% endif %}">

        {# 合計カバレッジ + 最終実行日時 #}
        <div class="row mb-4 fade-in">
            <div class="col-md-4">
                <div class="card border-secondary text-center py-4">
                    <div class="card-body">
                        <div id="totalPct" class="display-3 fw-bold" style="color:#234;">
                            {{ coverage.total_pct if coverage else 0 }}%
                        </div>
                        <p class="text-body-secondary mb-1">総カバレッジ</p>
                        <small id="covStmts" class="text-body-secondary">
                            {{ coverage.total_covered if coverage else 0 }} /
                            {{ coverage.total_stmts if coverage else 0 }} ステートメント
                        </small>
                    </div>
                </div>
            </div>
            <div class="col-md-8 d-flex align-items-center">
                <div class="w-100">
                    <div class="d-flex justify-content-between mb-1">
                        <small class="text-body-secondary">カバレッジ進捗</small>
                        <small id="lastRun" class="text-body-secondary">
                            最終実行: {{ coverage.last_run if coverage else '' }}
                        </small>
                    </div>
                    <div class="progress" style="height:20px;">
                        <div id="totalBar" class="progress-bar bg-secondary"
                             style="width:{{ coverage.total_pct if coverage else 0 }}%;">
                        </div>
                    </div>
                    <div class="d-flex justify-content-between mt-2">
                        <small class="text-body-secondary">0%</small>
                        <small class="text-body-secondary">目標: 50%</small>
                        <small class="text-body-secondary">100%</small>
                    </div>
                </div>
            </div>
        </div>

        {# ファイル別テーブル #}
        <div class="card border-secondary fade-in">
            <div class="card-header">
                <i class="fa fa-table me-2"></i>ファイル別カバレッジ
            </div>
            <div class="card-body p-0">
                <table class="table table-sm table-hover mb-0" id="coverageTable">
                    <thead class="table-light">
                        <tr>
                            <th class="ps-3">ファイル</th>
                            <th class="text-end" style="width:80px;">Stmts</th>
                            <th class="text-end" style="width:80px;">Miss</th>
                            <th style="width:200px;">カバレッジ</th>
                        </tr>
                    </thead>
                    <tbody id="coverageTableBody">
                        {% if coverage %}
                        {% for f in coverage.files %}
                        <tr>
                            <td class="ps-3 font-monospace small">{{ f.name }}</td>
                            <td class="text-end small">{{ f.stmts }}</td>
                            <td class="text-end small text-body-secondary">{{ f.missing }}</td>
                            <td>
                                <div class="d-flex align-items-center gap-2">
                                    <div class="progress flex-grow-1" style="height:8px;">
                                        <div class="progress-bar {% if f.pct >= 70 %}bg-secondary{% elif f.pct >= 40 %}bg-secondary opacity-75{% else %}bg-secondary opacity-50{% endif %}"
                                             style="width:{{ f.pct }}%;"></div>
                                    </div>
                                    <small style="width:36px;text-align:right;">{{ f.pct }}%</small>
                                </div>
                            </td>
                        </tr>
                        {% endfor %}
                        {% endif %}
                    </tbody>
                </table>
            </div>
        </div>

    </div>{# /coverageResult #}

</div>
{% endblock %}
```

**Step 2: Flask がテンプレートをレンダリングできるか確認**

アプリを起動してブラウザで `http://127.0.0.1:5000/admin/coverage` にアクセス（または `curl`）:

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo && "C:/Users/arihi/miniconda3/envs/flask2_env/python.exe" -c "
from app import create_app
app = create_app({'TESTING': True, 'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:', 'WTF_CSRF_ENABLED': False, 'STRIPE_SECRET_KEY': ''})
with app.test_client() as c:
    with app.app_context():
        from models import db
        db.create_all()
        # 管理者ユーザーでログインが必要なため、テンプレートのレンダリングのみ確認
        from flask import render_template
        with app.test_request_context():
            html = render_template('admin/coverage.j2', coverage=None, SITE_NAME='test', GLOBAL_NAV_PAGES={}, FOOTER_NAV_PAGES={})
            print('OK:', len(html), 'chars')
"
```
期待: `OK: XXXX chars`

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2 && git add Memo/templates/admin/coverage.j2 && git commit -m "feat: add admin coverage template"
```

---

### Task 3: sidemenu.j2 の href を更新する

**Files:**
- Modify: `templates/admin/sidemenu.j2:17`

**Step 1: sidemenu.j2 の17行目を更新する（Edit ツール）**

変更対象:
```html
        <li class="nav-item fade-in fade-in-delay-11"><a class="nav-link text-body-secondary fs-5 {% if request.endpoint == '' %}active{% endif %}" href=""><i class="fa fa-table me-2"></i>テスト網羅率状況</a></li>
```

変更後:
```html
        <li class="nav-item fade-in fade-in-delay-11"><a class="nav-link text-body-secondary fs-5 {% if request.endpoint == 'admin.coverage' %}active{% endif %}" href="{{ url_for('admin.coverage') }}"><i class="fa fa-table me-2"></i>テスト網羅率状況</a></li>
```

**Step 2: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2 && git add Memo/templates/admin/sidemenu.j2 && git commit -m "feat: link coverage menu item to admin.coverage route"
```

---

### Task 4: main.js にテスト実行ボタンの AJAX ハンドラを追加する

**Files:**
- Modify: `static/js/main.js`（末尾 `})();` の直前に追記）

**Step 1: main.js の末尾（最後の `})();` の直前）に以下を追記する**

`old_string` として現在の末尾のコードを特定して Edit ツールで追記:

```javascript
    observer.observe(firstTrack);
})();
```

を以下に置き換え:

```javascript
    observer.observe(firstTrack);
})();

/* =========================
  テスト網羅率 実行ボタン
========================== */
(() => {
    const runBtn = document.getElementById('coverageRunBtn');
    if (!runBtn) return;

    const loading   = document.getElementById('coverageLoading');
    const emptyMsg  = document.getElementById('coverageEmpty');
    const result    = document.getElementById('coverageResult');
    const totalPct  = document.getElementById('totalPct');
    const covStmts  = document.getElementById('covStmts');
    const lastRun   = document.getElementById('lastRun');
    const totalBar  = document.getElementById('totalBar');
    const tableBody = document.getElementById('coverageTableBody');

    runBtn.addEventListener('click', async () => {
        if (!confirm('pytest を実行します。数秒〜数十秒かかります。よろしいですか？')) return;

        // ローディング表示
        runBtn.disabled = true;
        loading.classList.remove('d-none');
        emptyMsg.classList.add('d-none');
        result.classList.add('d-none');

        try {
            const res = await fetch('/admin/coverage/run', {
                method: 'POST',
                headers: { 'X-CSRFToken': document.querySelector('meta[name=csrf-token]')?.content || '' },
            });
            const data = await res.json();

            if (!data.ok) {
                alert('エラー: ' + (data.error || '不明なエラー'));
                return;
            }

            const cov = data.coverage;

            // 合計カバレッジ更新
            totalPct.textContent = cov.total_pct + '%';
            covStmts.textContent = cov.total_covered + ' / ' + cov.total_stmts + ' ステートメント';
            lastRun.textContent  = '最終実行: ' + cov.last_run;
            totalBar.style.width = cov.total_pct + '%';

            // テーブル再描画
            tableBody.innerHTML = cov.files.map(f => `
                <tr>
                    <td class="ps-3 font-monospace small">${f.name}</td>
                    <td class="text-end small">${f.stmts}</td>
                    <td class="text-end small text-body-secondary">${f.missing}</td>
                    <td>
                        <div class="d-flex align-items-center gap-2">
                            <div class="progress flex-grow-1" style="height:8px;">
                                <div class="progress-bar bg-secondary${f.pct < 40 ? ' opacity-50' : f.pct < 70 ? ' opacity-75' : ''}"
                                     style="width:${f.pct}%;"></div>
                            </div>
                            <small style="width:36px;text-align:right;">${f.pct}%</small>
                        </div>
                    </td>
                </tr>
            `).join('');

            // 結果表示
            emptyMsg.classList.add('d-none');
            result.classList.remove('d-none');

        } catch (e) {
            alert('通信エラー: ' + e.message);
        } finally {
            loading.classList.add('d-none');
            runBtn.disabled = false;
        }
    });
})();
```

**Step 2: JavaScript 構文エラーがないか確認**

```bash
"C:/Users/arihi/miniconda3/envs/flask2_env/python.exe" -c "
import subprocess
r = subprocess.run(['node', '--check', 'static/js/main.js'], capture_output=True, text=True, cwd='C:/Users/arihi/Dropbox/DevOps/Flask/Percial2/Memo')
print(r.stdout or r.stderr or 'OK')
"
```

node がない場合は省略可。ブラウザで動作確認する。

**Step 3: コミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2 && git add Memo/static/js/main.js && git commit -m "feat: add coverage run button AJAX handler to main.js"
```

---

## 動作確認チェックリスト

- [ ] `/admin/coverage` にアクセスすると既存データ（または未実行メッセージ）が即時表示される
- [ ] 「テスト実行」ボタンを押すとスピナーが表示される
- [ ] 数十秒後にカバレッジ結果がページに反映される
- [ ] ファイル別テーブルにプログレスバーと % が表示される
- [ ] サイドメニューの「テスト網羅率状況」リンクが機能している
- [ ] カレント表示（active）がサイドメニューで正しく適用される
