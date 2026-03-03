# Admin Glow Effect Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 管理画面のカード背景とサイドバーナビリンクに「ダーク×グロー」エフェクトを追加し、高級感を演出する。

**Architecture:** `style.css` の管理画面セクションに CSS のみで追記。`.adminMain .card` を対象にした内側発光とボーダーグロー、`.sidebarMenu .nav-link` を対象にしたホバー時の左ボーダー発光＋局所 radial-gradient。テンプレート・JS の変更なし。

**Tech Stack:** CSS (box-shadow, radial-gradient, ::before pseudo-element, transition)

---

### Task 1: カード内側グロー + ボーダーグロー

**Files:**
- Modify: `static/css/style.css`（管理画面セクション末尾に追記）

ダーク環境でのカードに「奥行き感」を出す。
- `box-shadow: inset` で内側から薄く光らせる
- `border` を半透明グロー系に変更
- ホバー時にわずかに強調

**Step 1: style.css の管理画面セクション末尾（`/* ============== 管理画面 =============== */` ブロックの最後）に以下を追記**

```css
/* 管理コンテンツ カードグロー */

.adminMain .card {
    background-color: #0e1a27;
    border: 1px solid rgba(58, 104, 136, 0.25) !important;
    box-shadow:
        inset 0 0 20px rgba(20, 40, 60, 0.6),
        0 2px 12px rgba(0, 0, 0, 0.4),
        0 0 0 1px rgba(58, 104, 136, 0.08);
    transition: box-shadow 0.35s ease, border-color 0.35s ease;
}

.adminMain .card:hover {
    border-color: rgba(58, 104, 136, 0.5) !important;
    box-shadow:
        inset 0 0 28px rgba(20, 40, 60, 0.7),
        0 4px 20px rgba(0, 0, 0, 0.5),
        0 0 18px rgba(58, 104, 136, 0.12);
}

.adminMain .card-header {
    background-color: rgba(20, 35, 55, 0.9);
    border-bottom: 1px solid rgba(58, 104, 136, 0.2);
}

/* ライトテーマ上書き */
[data-bs-theme="light"] .adminMain .card {
    background-color: #f4f6f8;
    border: 1px solid rgba(100, 130, 160, 0.2) !important;
    box-shadow:
        inset 0 0 12px rgba(180, 200, 220, 0.3),
        0 2px 8px rgba(0, 0, 0, 0.08);
}

[data-bs-theme="light"] .adminMain .card:hover {
    border-color: rgba(80, 120, 160, 0.4) !important;
    box-shadow:
        inset 0 0 16px rgba(180, 200, 220, 0.4),
        0 4px 14px rgba(0, 0, 0, 0.1),
        0 0 12px rgba(80, 120, 160, 0.08);
}

[data-bs-theme="light"] .adminMain .card-header {
    background-color: rgba(220, 228, 236, 0.8);
    border-bottom: 1px solid rgba(100, 130, 160, 0.2);
}
```

**Step 2: ブラウザで確認**
- `http://127.0.0.1:5000/admin/` を開く
- カードに暗い内側グロー＋薄いボーダーがあること
- ホバー時にボーダーが少し明るくなること
- ライトモード切替でも破綻しないこと

---

### Task 2: サイドバー ナビリンク ホバーグロー

**Files:**
- Modify: `static/css/style.css`（Task 1 の追記の直後に続けて追記）

左ボーダーが光り、背景が局所的に発光するホバー効果。

**Step 1: 以下を続けて追記**

```css
/* サイドバー ナビリンク ホバーグロー */

.sidebarMenu .nav-link {
    position: relative;
    border-left: 2px solid transparent;
    padding-left: 1.1rem;
    transition:
        color 0.25s ease,
        border-color 0.25s ease,
        background 0.25s ease;
}

.sidebarMenu .nav-link::before {
    content: "";
    position: absolute;
    inset: 0;
    background: radial-gradient(
        ellipse at 20% 50%,
        rgba(58, 104, 136, 0.12) 0%,
        transparent 70%
    );
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
    border-radius: 0.375rem;
}

.sidebarMenu .nav-link:hover {
    color: #b8d0e8 !important;
    border-left-color: rgba(58, 104, 136, 0.6);
}

.sidebarMenu .nav-link:hover::before {
    opacity: 1;
}

/* アクティブリンク：常時点灯 */
.sidebarMenu .nav-link.active {
    color: #d0e4f4 !important;
    border-left-color: #3a6888 !important;
    border-left-width: 3px;
    text-shadow: 0 0 8px rgba(58, 104, 136, 0.5);
}

.sidebarMenu .nav-link.active::before {
    opacity: 1;
    background: radial-gradient(
        ellipse at 20% 50%,
        rgba(58, 104, 136, 0.18) 0%,
        transparent 70%
    );
}

/* ライトテーマ上書き */
[data-bs-theme="light"] .sidebarMenu .nav-link:hover {
    color: #234 !important;
    border-left-color: rgba(35, 68, 100, 0.5);
}

[data-bs-theme="light"] .sidebarMenu .nav-link::before {
    background: radial-gradient(
        ellipse at 20% 50%,
        rgba(35, 68, 100, 0.08) 0%,
        transparent 70%
    );
}

[data-bs-theme="light"] .sidebarMenu .nav-link.active {
    color: #1a3a5c !important;
    border-left-color: #3a6888 !important;
    text-shadow: none;
}
```

**Step 2: ブラウザで確認**
- サイドバーのリンクにホバーすると左ボーダーが光り、背景が微かに発光すること
- アクティブページのリンクが常時ハイライトされていること
- ライトモード切替でも色が適切に変わること

---

### Task 3: コミット

**Step 1: 変更を確認してコミット**

```bash
cd C:/Users/arihi/Dropbox/DevOps/Flask/Percial2
git add Memo/static/css/style.css
git commit -m "style: 管理画面にグローエフェクト追加（カード内側発光・ナビリンクホバー）"
```
