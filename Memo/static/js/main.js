(() => {
    "use strict";

    console.log("🔥 main.js loaded");

    /* =========================
      カラーモード
    ========================== */

    const getStoredTheme = () => localStorage.getItem("theme");
    const setStoredTheme = (theme) => localStorage.setItem("theme", theme);

    const getPreferredTheme = () => {
        const storedTheme = getStoredTheme();
        if (storedTheme) return storedTheme;
        return window.matchMedia("(prefers-color-scheme: dark)").matches
            ? "dark"
            : "light";
    };

    const setTheme = (theme) => {
        if (theme === "auto") {
            document.documentElement.setAttribute(
                "data-bs-theme",
                window.matchMedia("(prefers-color-scheme: dark)").matches
                    ? "dark"
                    : "light",
            );
        } else {
            document.documentElement.setAttribute("data-bs-theme", theme);
        }
    };

    setTheme(getPreferredTheme());

    const showActiveTheme = (theme, focus = false) => {
        const themeSwitcher = document.querySelector("#bd-theme");
        if (!themeSwitcher) return;

        const themeSwitcherText = document.querySelector("#bd-theme-text");
        const activeThemeIcon = document.querySelector(
            ".theme-icon-active use",
        );
        const btnToActive = document.querySelector(
            `[data-bs-theme-value="${theme}"]`,
        );
        const svgOfActiveBtn = btnToActive
            .querySelector("svg use")
            .getAttribute("href");

        document
            .querySelectorAll("[data-bs-theme-value]")
            .forEach((element) => {
                element.classList.remove("active");
                element.setAttribute("aria-pressed", "false");
            });

        btnToActive.classList.add("active");
        btnToActive.setAttribute("aria-pressed", "true");
        activeThemeIcon.setAttribute("href", svgOfActiveBtn);

        const themeSwitcherLabel = `${themeSwitcherText.textContent} (${btnToActive.dataset.bsThemeValue})`;
        themeSwitcher.setAttribute("aria-label", themeSwitcherLabel);

        if (focus) themeSwitcher.focus();
    };

    /* =========================
      DOMContentLoaded
    ========================== */

    window.addEventListener("DOMContentLoaded", () => {
        console.log("🔥 DOMContentLoaded");

        showActiveTheme(getPreferredTheme());

        document.querySelectorAll("[data-bs-theme-value]").forEach((toggle) => {
            toggle.addEventListener("click", () => {
                const theme = toggle.getAttribute("data-bs-theme-value");
                setStoredTheme(theme);
                setTheme(theme);
                showActiveTheme(theme, true);
            });
        });

        // pre要素内コードハイライト
        hljs.highlightAll();
        hljs.initLineNumbersOnLoad();

        // スクロールフェードイン
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("is-visible");
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.1 },
        );

        document
            .querySelectorAll(".fade-in")
            .forEach((el) => observer.observe(el));

        // 管理画面のテーブル行クリック
        const tbody = document.querySelector("tbody");
        if (tbody) {
            tbody.addEventListener("click", (e) => {
                if (e.target.closest(".action-btn")) return;
                const row = e.target.closest(".clickable-row");
                if (!row?.dataset.href) return;
                window.location.href = row.dataset.href;
            });

            tbody.addEventListener("keydown", (e) => {
                if (e.key !== "Enter") return;
                const row = e.target.closest(".clickable-row");
                if (row?.dataset.href) window.location.href = row.dataset.href;
            });
        }

        // チェックボックス表示制御
        const toggleVisible = (checkId, areaId) => {
            const check = document.getElementById(checkId);
            const area = document.getElementById(areaId);
            if (!check || !area) return;
            const update = () =>
                area.classList.toggle("is-visible", check.checked);
            update();
            check.addEventListener("change", update);
        };

        toggleVisible("changePasswordCheck", "password-area");
        toggleVisible("deleteUserCheck", "delete-area");

        // EasyMDEマークダウンエディタ
        if (typeof EasyMDE !== "undefined" && document.getElementById("content")) {
            new EasyMDE({
                element: document.getElementById("content"),
                spellChecker: false,
                autofocus: true,
                placeholder: "Markdownで本文を入力してください",
            });
        }

        // 404翻訳ボタン
        const translateBtn = document.getElementById("translate-btn");
        if (translateBtn) {
            translateBtn.addEventListener("click", async () => {
                const target = document.getElementById("error-text");
                const text = target.innerText;
                try {
                    const res = await fetch(
                        "https://translate.googleapis.com/translate_a/single" +
                        "?client=gtx&sl=auto&tl=ja&dt=t&q=" + encodeURIComponent(text),
                    );
                    const data = await res.json();
                    target.innerText = data[0].map((item) => item[0]).join("");
                } catch (e) {
                    console.error("Translation failed:", e);
                }
            });
        }

        // ステップバーアニメーション（admin/login）
        const barDelays = { "delay-1": 300, "delay-2": 1050, "delay-3": 1800 };
        Object.keys(barDelays).forEach((cls) => {
            const bar = document.querySelector(".step-bar.done." + cls);
            if (!bar) return;
            const fill = bar.querySelector(".progress-bar");
            setTimeout(() => {
                fill.style.transition = "width 0.65s ease";
                fill.style.width = "100%";
            }, barDelays[cls]);
        });
    });
})();

/* =========================
    グローバルクリック一元管理
========================== */

const ACTIONS = {
    // 前のページに戻る
    back: (e, el) => {
        e.preventDefault();
        history.back();
    },

    // トップへスクロール
    scrollTop: (e, el) => {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: "smooth" });
    },

    // ========= カテゴリ =========
    category: (e, badge) => {
        e.preventDefault();

        const wrapper = document.getElementById("category-wrapper");
        if (!wrapper?.contains(badge)) return;

        const MAX = 3;
        const error = document.getElementById("category-error");

        const allBadges = wrapper.querySelectorAll(".category-badge");
        const index = Array.from(allBadges).indexOf(badge);
        const checkboxes = wrapper.querySelectorAll(".category-checkbox");
        const checkbox = checkboxes[index];

        const checkedCount = wrapper.querySelectorAll(
            ".category-checkbox:checked",
        ).length;

        if (!checkbox.checked && checkedCount >= MAX) {
            error?.classList.remove("d-none");
            return;
        }

        error?.classList.add("d-none");
        checkbox.checked = !checkbox.checked;
        badge.classList.toggle("selected", checkbox.checked);
    },

    // ========= いいね =========
    like: async (e, btn) => {
        e.preventDefault();

        const container = btn.closest(".like-area");
        const memoId = container.dataset.memoId;
        const action = btn.dataset.action;

        const url =
            action === "add"
                ? `/favorite/add/${memoId}`
                : `/favorite/remove/${memoId}`;

        const res = await fetch(url, {
            method: "POST",
            headers: { "X-Requested-With": "XMLHttpRequest" },
        });

        if (!res.ok) return;

        const data = await res.json();

        btn.classList.toggle("active", data.liked);
        btn.dataset.action = data.liked ? "remove" : "add";
        btn.innerHTML =
            (data.liked
                ? "<i class='fa fa-heart' style='color:#e06'></i>"
                : "<i class='fa fa-heart-o' style='color:#666'></i>") +
            ` <span class="like-count text-body-secondary">${data.like_count}いいね</span>`;
    },
};

/* =========================
    クリックルーター
========================== */

document.addEventListener("click", (e) => {
    // data-action方式
    const actionEl = e.target.closest("[data-action]");
    if (actionEl) {
        const actionName = actionEl.dataset.action;
        const handler = ACTIONS[actionName];
        if (handler) handler(e, actionEl);
        return;
    }

    // 既存クラス方式
    const badge = e.target.closest(".category-badge");
    if (badge) {
        ACTIONS.category(e, badge);
        return;
    }

    const likeBtn = e.target.closest(".btn-like");
    if (likeBtn) {
        ACTIONS.like(e, likeBtn);
        return;
    }
});
