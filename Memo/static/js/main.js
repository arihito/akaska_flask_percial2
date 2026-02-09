(() => {
    'use strict';

    // カラーモード
    const getStoredTheme = () => localStorage.getItem('theme')
    const setStoredTheme = theme => localStorage.setItem('theme', theme)

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme()
        if (storedTheme) {
        return storedTheme
        }

        return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
    }

    const setTheme = theme => {
        if (theme === 'auto') {
        document.documentElement.setAttribute('data-bs-theme', (window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'))
        } else {
        document.documentElement.setAttribute('data-bs-theme', theme)
        }
    }

    setTheme(getPreferredTheme())

    const showActiveTheme = (theme, focus = false) => {
        const themeSwitcher = document.querySelector('#bd-theme')

        if (!themeSwitcher) {
        return
        }

        const themeSwitcherText = document.querySelector('#bd-theme-text')
        const activeThemeIcon = document.querySelector('.theme-icon-active use')
        const btnToActive = document.querySelector(`[data-bs-theme-value="${theme}"]`)
        const svgOfActiveBtn = btnToActive.querySelector('svg use').getAttribute('href')

        document.querySelectorAll('[data-bs-theme-value]').forEach(element => {
        element.classList.remove('active')
        element.setAttribute('aria-pressed', 'false')
        })

        btnToActive.classList.add('active')
        btnToActive.setAttribute('aria-pressed', 'true')
        activeThemeIcon.setAttribute('href', svgOfActiveBtn)
        const themeSwitcherLabel = `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`
        themeSwitcher.setAttribute('aria-label', themeSwitcherLabel)

        if (focus) {
        themeSwitcher.focus()
        }
    }

    window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', () => {
        const storedTheme = getStoredTheme()
        if (storedTheme !== 'light' && storedTheme !== 'dark') {
        setTheme(getPreferredTheme())
        }
    })

    // ページが読み込まれた実行
    window.addEventListener('DOMContentLoaded', () => {

        // カラーモード
        showActiveTheme(getPreferredTheme())

        document.querySelectorAll('[data-bs-theme-value]')
        .forEach(toggle => {
            toggle.addEventListener('click', () => {
            const theme = toggle.getAttribute('data-bs-theme-value')
            setStoredTheme(theme)
            setTheme(theme)
            showActiveTheme(theme, true)
            })
        })

        // pre要素内コードハイライト
        hljs.highlightAll();
        hljs.initLineNumbersOnLoad();

        // スクロールフェードイン
        const observer = new IntersectionObserver(entries => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('is-visible');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });

        document.querySelectorAll('.fade-in').forEach(el => {
            observer.observe(el);
        });

        // 管理画面のテーブル行クリック
        const tbody = document.querySelector('tbody');
        if (!tbody) return;

        tbody.addEventListener('click', (e) => {

            // 内包ボタンはクリック範囲を除外
            if (e.target.closest('.action-btn')) return;

            const row = e.target.closest('.clickable-row');
            if (!row || !row.dataset.href) return;

            console.log('row click:', row.dataset.href);
            window.location.href = row.dataset.href;
        });

        // エンターキーでも実行可能
        tbody.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter') return;
            const row = e.target.closest('.clickable-row');
            if (row?.dataset.href) {
                window.location.href = row.dataset.href;
            }
        });

        // ボタンクリックはテーブル行に伝播させない
        document.querySelectorAll('.action-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
            });
        });

        // チェックボックスをオンにした時だけパスワード変更フォームを表示
        const pass_check = document.getElementById('changePasswordCheck');
        const pass_area = document.getElementById('password-area');
        const toggle = () => {
            if (pass_check?.checked) {
                pass_area.classList.add('is-visible');
            } else {
                pass_area.classList.remove('is-visible');
            }
        };
        // 初期表示（バリデーションエラー対応）
        toggle();
        pass_check.addEventListener('change', toggle);

        // ユーザー削除ボタンのフェードイン表示
        const del_check = document.getElementById('deleteUserCheck');
        const del_area  = document.getElementById('delete-area');

        if (!del_check || !del_area) return;

        del_area.classList.remove('is-visible');

        del_check.addEventListener('change', () => {
            del_area.classList.toggle('is-visible', del_check.checked);
        });
    })
})()

// ユーザー削除ボタン
document.getElementById('deleteUserCheck')?.addEventListener('change', function () {
    const area = document.getElementById('delete-button-area');
    if (this.checked) {
        area.classList.remove('d-none');
    } else {
        area.classList.add('d-none');
    }
});

// トップに戻るアニメーションボタン
document.getElementById('scrollTopBtn')?.addEventListener('click', () => {
  window.scrollTo({
    top: 0,
    behavior: 'smooth'
  });
});

// 前のページに戻るボタンクリック
document.getElementById('backBtn')?.addEventListener('click', e => {
    e.preventDefault();
    history.back();
});

// いいねアイコンクリック
document.addEventListener("click", async function (e) {
console.log("###################DOC CLICK#################", e.target);
    const btn = e.target.closest(".btn-like");
    if (!btn) return;

    const container = btn.closest(".like-area");
    const memoId = container.dataset.memoId;
    const action = btn.dataset.action;

    const url = action === "add"
        ? `/favorite/add/${memoId}`
        : `/favorite/remove/${memoId}`;

    const res = await fetch(url, {
        method: "POST",
        headers: {
            "X-Requested-With": "XMLHttpRequest"
        }
    });

    if (!res.ok) return;

    const data = await res.json();

    // UI 更新
    btn.classList.toggle("active", data.liked);
    btn.dataset.action = data.liked ? "remove" : "add";
    btn.innerHTML = (data.liked ? "<i class='fa fa-heart' style='color:#e06'></i>" : "<i class='fa fa-heart-o' style='color:#666'></i>")
        + ` <span class="like-count text-body-secondary">${data.like_count}いいね</span>`;

    animateHeart(btn);
});

// ハートアニメーション
function animateHeart(btn) {
    const rect = btn.getBoundingClientRect();
    const heart = document.createElement("div");
    heart.className = "heart-burst";
    heart.textContent = "❤️";

    heart.style.left = rect.left + window.scrollX + "px";
    heart.style.top  = rect.top + window.scrollY + "px";

    document.body.appendChild(heart);
    setTimeout(() => heart.remove(), 600);
}
