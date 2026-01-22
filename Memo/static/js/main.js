(() => {
    'use strict'

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

    window.addEventListener('DOMContentLoaded', () => {
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
    })
    })()

    document.addEventListener("click", async function (e) {
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
    btn.innerHTML = (data.liked ? "❤️" : "🤍")
        + ` <span class="like-count">${data.like_count}</span>`;

    // ハートアニメーション
    animateHeart(btn);
});
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