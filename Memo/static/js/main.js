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
        toggleVisible("summaryCheck", "summary-area");

        // 要約文フィールドに初期値がある場合（固定ページからのリダイレクト等）はスイッチを自動ON
        const summaryCheck = document.getElementById("summaryCheck");
        const summaryField = document.getElementById("summary");
        if (summaryCheck && summaryField && summaryField.value.trim() !== "") {
            summaryCheck.checked = true;
            summaryCheck.dispatchEvent(new Event("change"));
        }

        // EasyMDEマークダウンエディタ（固定ページ生成からの引き継ぎ初期値対応）
        if (typeof EasyMDE !== "undefined" && document.getElementById("content")) {
            const contentEl = document.getElementById("content");
            const initBody = contentEl.dataset.initBody || "";
            new EasyMDE({
                element: contentEl,
                spellChecker: false,
                autofocus: true,
                placeholder: "Markdownで本文を入力してください",
                initialValue: initBody || undefined,
            });
        }

        // 固定ページ生成: 「保存後に投稿作成ページへ移動する」チェックボックスとhidden inputの同期
        const redirectMemoCheck = document.getElementById("fc-redirect-memo-check");
        const redirectMemoHidden = document.getElementById("fc-redirect-to-memo");
        if (redirectMemoCheck && redirectMemoHidden) {
            redirectMemoCheck.addEventListener("change", function () {
                redirectMemoHidden.value = this.checked ? "1" : "";
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

        // Bootstrapツールチップの初期化
        document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            new bootstrap.Tooltip(el, { html: true });
        });

        // カテゴリー削除確認（admin/category）
        document.querySelectorAll(".cat-delete-form").forEach((form) => {
            form.addEventListener("submit", (e) => {
                if (!confirm("このカテゴリーを削除しますか？")) e.preventDefault();
            });
        });

        // カテゴリー追加フォームバリデーション（admin/category）
        const catForm = document.getElementById("category-add-form");
        if (catForm) {
            const nameInput  = document.getElementById("cat-name");
            const colorInput = document.getElementById("cat-color");
            const nameError  = document.getElementById("cat-name-error");
            const colorError = document.getElementById("cat-color-error");
            const submitBtn  = document.getElementById("cat-submit");

            // #666の輝度しきい値（0.299*102 + 0.587*102 + 0.114*102 = 102）
            const COLOR_LIMIT = 102;

            const hexToRgb = (hex) => {
                const r = parseInt(hex.slice(1, 3), 16);
                const g = parseInt(hex.slice(3, 5), 16);
                const b = parseInt(hex.slice(5, 7), 16);
                return { r, g, b };
            };

            const getLuminance = (hex) => {
                const { r, g, b } = hexToRgb(hex);
                return 0.299 * r + 0.587 * g + 0.114 * b;
            };

            const validateName = () => {
                const val = nameInput.value;
                if (!val) {
                    nameError.textContent = "カテゴリー名を入力してください";
                    nameError.classList.remove("d-none");
                    return false;
                }
                if (!/^[A-Za-z0-9]{1,12}$/.test(val)) {
                    nameError.textContent = "英数字のみ・12文字以内で入力してください";
                    nameError.classList.remove("d-none");
                    return false;
                }
                nameError.classList.add("d-none");
                return true;
            };

            const validateColor = () => {
                const lum = getLuminance(colorInput.value);
                if (lum >= COLOR_LIMIT) {
                    colorError.textContent = "#666より暗い色を選択してください";
                    colorError.classList.remove("d-none");
                    return false;
                }
                colorError.classList.add("d-none");
                return true;
            };

            nameInput.addEventListener("input", () => {
                validateName();
                submitBtn.disabled = !validateName() || !validateColor();
            });

            colorInput.addEventListener("input", () => {
                validateColor();
                submitBtn.disabled = !validateName() || !validateColor();
            });

            catForm.addEventListener("submit", (e) => {
                const nameOk  = validateName();
                const colorOk = validateColor();
                if (!nameOk || !colorOk) e.preventDefault();
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
    管理画面ヘッダー：AIポイント即時反映
========================== */
/**
 * AI操作成功後にヘッダーの残ポイント表示をリアルタイム更新する。
 * サーバーレスポンスの remaining_points が null/undefined の場合（スーパーアドミン）は何もしない。
 * @param {number|null} remaining - サーバーから返却された残ポイント数
 */
function getBatteryLevel(points) {
    if (points >= 19) return 4;
    if (points >= 13) return 3;
    if (points >= 7)  return 2;
    if (points >= 1)  return 1;
    return 0;
}

function updateAdminPoints(remaining) {
    if (remaining === null || remaining === undefined) return;
    // ヘッダー内の残ポイント表示要素（battery アイコン直後の strong）を特定
    const ptEl = document.querySelector(".admin-navbar .border strong:first-of-type");
    if (!ptEl) return;
    ptEl.textContent = remaining;
    // 残5pt以下なら赤文字に切り替え
    if (remaining <= 5) {
        ptEl.classList.add("text-danger");
    }
    // バッテリーアイコンをポイント段階に応じて更新
    const icon = ptEl.previousElementSibling;
    if (icon && icon.classList.contains("fa")) {
        const level = getBatteryLevel(remaining);
        icon.className = icon.className.replace(/fa-battery-\d/, `fa-battery-${level}`);
        icon.style.color = level === 0 ? "#900" : "";
    }
}

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
    AI生成ボタン（admin/category）
========================== */
document.addEventListener("DOMContentLoaded", () => {
    const catAiGenBtn = document.getElementById("catAiGenBtn");
    if (!catAiGenBtn) return;

    catAiGenBtn.addEventListener("click", async () => {
        if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;

        const nameInput  = document.getElementById("cat-name");
        const colorInput = document.getElementById("cat-color");
        const icon       = document.getElementById("catAiGenBtnIcon");
        const loading    = document.getElementById("catAiGenLoading");
        const errorEl    = document.getElementById("catAiGenError");
        const csrfToken  = document.querySelector('input[name="csrf_token"]')?.value || "";

        catAiGenBtn.disabled = true;
        icon?.classList.add("d-none");
        loading?.classList.remove("d-none");
        errorEl?.classList.add("d-none");

        try {
            const res = await fetch("/admin/category/ai_suggest", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({}),
            });

            const json = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(json.message || `HTTP ${res.status}`);

            if (json.status === "ok") {
                if (nameInput)  nameInput.value  = json.name;
                if (colorInput) colorInput.value = json.color;
                updateAdminPoints(json.remaining_points);
            } else {
                throw new Error(json.message || "AI生成エラー");
            }
        } catch (e) {
            console.error("######## カテゴリーAI生成エラー ########", e);
            if (errorEl) {
                errorEl.textContent = e.message || "エラーが発生しました";
                errorEl.classList.remove("d-none");
            }
        } finally {
            catAiGenBtn.disabled = false;
            icon?.classList.remove("d-none");
            loading?.classList.add("d-none");
        }
    });
});

/* =========================
    AI生成ボタン（admin/user_thumb）
========================== */
document.addEventListener("DOMContentLoaded", () => {
    const thumbAiGenBtn = document.getElementById("thumbAiGenBtn");
    if (!thumbAiGenBtn) return;

    thumbAiGenBtn.addEventListener("click", async () => {
        if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;

        const preview  = document.getElementById("thumbAiPreview");
        const loading  = document.getElementById("thumbAiLoading");
        const errorEl  = document.getElementById("thumbAiError");
        const userSel  = document.getElementById("thumb-ai-user-select");
        const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || "";

        thumbAiGenBtn.disabled = true;
        loading?.classList.remove("d-none");
        errorEl?.classList.add("d-none");

        try {
            const res = await fetch("/admin/user_thumb/ai_generate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-Requested-With": "XMLHttpRequest",
                    "X-CSRFToken": csrfToken,
                },
                body: JSON.stringify({
                    user_id: userSel?.value ? parseInt(userSel.value) : null,
                }),
            });

            const json = await res.json().catch(() => ({}));
            if (!res.ok) throw new Error(json.message || `HTTP ${res.status}`);

            if (json.status === "ok") {
                updateAdminPoints(json.remaining_points);
                // プレビューをデフォルトアイコンから生成画像に差し替えて拡大表示
                if (preview) {
                    preview.src = json.url + "?t=" + Date.now();
                    preview.style.width  = "160px";
                    preview.style.height = "160px";
                    preview.style.borderRadius = "12px";
                }

                // サムネイル表示設定グリッドに動的追加
                const container = document.querySelector(".thumbnail-select");
                if (container) {
                    const uid  = "tc-ai-" + Date.now();
                    const item = document.createElement("div");
                    item.className = "thumb-item";
                    item.dataset.filename = json.filename;
                    item.innerHTML = `
                        <input type="hidden" name="delete_thumbs" value="${json.filename}" class="thumb-delete-input" disabled>
                        <input type="checkbox" name="visible_thumbs" id="${uid}" value="${json.filename}" class="d-none" checked>
                        <label for="${uid}" class="thumb-label position-relative d-block">
                            <img src="${json.url}?t=${Date.now()}" alt="${json.filename}" class="thumb-img" width="" height="">
                            <div class="thumb-delete-overlay"><i class="fa fa-times"></i></div>
                        </label>
                        <button type="button" class="thumb-delete-btn" title="削除"><i class="fa fa-trash-o"></i></button>
                        <div class="text-body-secondary text-center mt-1" style="font-size:0.65rem; word-break:break-all; width:80px;">${json.filename}</div>
                    `;
                    // 削除ボタンにイベントリスナーを付与（既存ロジックと同じ）
                    const delBtn = item.querySelector(".thumb-delete-btn");
                    delBtn.addEventListener("click", () => {
                        const overlay   = item.querySelector(".thumb-delete-overlay");
                        const hidden    = item.querySelector(".thumb-delete-input");
                        const isPending = overlay.classList.contains("is-visible");
                        if (isPending) {
                            overlay.classList.remove("is-visible");
                            hidden.disabled = true;
                            delBtn.innerHTML = '<i class="fa fa-trash-o"></i>';
                            delBtn.title = "削除";
                        } else {
                            overlay.classList.add("is-visible");
                            hidden.disabled = false;
                            delBtn.innerHTML = '<i class="fa fa-undo"></i>';
                            delBtn.title = "取り消し";
                        }
                    });
                    container.appendChild(item);
                }
            } else {
                throw new Error(json.message || "AI生成エラー");
            }
        } catch (e) {
            console.error("######## AI サムネイル生成エラー ########", e);
            if (errorEl) {
                errorEl.textContent = e.message || "エラーが発生しました";
                errorEl.classList.remove("d-none");
            }
        } finally {
            thumbAiGenBtn.disabled = false;
            loading?.classList.add("d-none");
        }
    });
});

/* =========================
    サムネイル削除ボタン（admin/user_thumb）
========================== */

document.addEventListener("DOMContentLoaded", () => {
    const visibilityForm = document.querySelector(".thumb-visibility-form");
    if (!visibilityForm) return;

    visibilityForm.querySelectorAll(".thumb-delete-btn").forEach((btn) => {
        btn.addEventListener("click", () => {
            const item    = btn.closest(".thumb-item");
            const overlay = item.querySelector(".thumb-delete-overlay");
            const hidden  = item.querySelector(".thumb-delete-input");
            const isPending = overlay.classList.contains("is-visible");

            if (isPending) {
                // 取り消し
                overlay.classList.remove("is-visible");
                hidden.disabled = true;
                btn.innerHTML = '<i class="fa fa-trash-o"></i>';
                btn.title = "削除";
            } else {
                // 削除フラグを立てる
                overlay.classList.add("is-visible");
                hidden.disabled = false;
                btn.innerHTML = '<i class="fa fa-undo"></i>';
                btn.title = "取り消し";
            }
        });
    });
});

/* =========================
    管理画面アナリティクスチャート
========================== */

document.addEventListener("DOMContentLoaded", () => {
    const barCanvas = document.getElementById("barChart");
    if (!barCanvas || !window.__CHART_DATA__) return;

    const chartData = window.__CHART_DATA__;

    // テーマ検出
    const isDark = () =>
        document.documentElement.getAttribute("data-bs-theme") === "dark";

    // テーマ別カラーパレット（彩度低め統一）
    const theme = () =>
        isDark()
            ? {
                  text: "#aaa",
                  subText: "#888",
                  gridLine: "rgba(255,255,255,0.06)",
                  borderPie: "#0d0f11",
                  legendBoxBorder: "#0d0f11",
                  barColors: [
                      "rgba(100, 110, 120, 0.75)",
                      "rgba(80, 95, 105, 0.75)",
                      "rgba(65, 80, 90, 0.75)",
                      "rgba(110, 125, 135, 0.75)",
                      "rgba(90, 100, 110, 0.75)",
                  ],
                  pieUserColors: [
                      "rgba(100, 110, 120, 0.8)",
                      "rgba(85, 95, 105, 0.8)",
                      "rgba(70, 80, 90, 0.8)",
                      "rgba(55, 65, 75, 0.8)",
                      "rgba(45, 52, 60, 0.8)",
                  ],
                  pieCatAlpha: "B3",
                  pieCatLighten: 0.2,
              }
            : {
                  text: "#555",
                  subText: "#777",
                  gridLine: "rgba(0,0,0,0.06)",
                  borderPie: "#fff",
                  legendBoxBorder: "#fff",
                  barColors: [
                      "rgba(140, 150, 160, 0.7)",
                      "rgba(120, 135, 145, 0.7)",
                      "rgba(105, 118, 130, 0.7)",
                      "rgba(155, 165, 172, 0.7)",
                      "rgba(130, 142, 150, 0.7)",
                  ],
                  pieUserColors: [
                      "rgba(140, 150, 160, 0.75)",
                      "rgba(120, 132, 142, 0.75)",
                      "rgba(105, 115, 125, 0.75)",
                      "rgba(90, 100, 110, 0.75)",
                      "rgba(78, 86, 95, 0.75)",
                  ],
                  pieCatAlpha: "99",
                  pieCatLighten: 0.2,
              };

    // 正規化: 配列中の最大値を100としてスケーリング
    const normalize = (values) => {
        const maxVal = Math.max(...values, 1);
        return values.map((v) => Math.round((v / maxVal) * 100));
    };

    // カテゴリー色を白方向へ20%ライトナー（#rrggbb → 各チャンネルを白に20%近づける）
    const lightenHex = (hex, amount) => {
        const r = parseInt(hex.slice(1, 3), 16);
        const g = parseInt(hex.slice(3, 5), 16);
        const b = parseInt(hex.slice(5, 7), 16);
        const lr = Math.min(255, Math.round(r + (255 - r) * amount));
        const lg = Math.min(255, Math.round(g + (255 - g) * amount));
        const lb = Math.min(255, Math.round(b + (255 - b) * amount));
        return `#${lr.toString(16).padStart(2, "0")}${lg.toString(16).padStart(2, "0")}${lb.toString(16).padStart(2, "0")}`;
    };

    // ---- 円グラフ1: カテゴリー分布 ----
    // 2秒遅延でフェードイン完了後にアニメーション開始
    let pieCatInstance = null;
    const pieCatCanvas = document.getElementById("pieCategory");
    if (pieCatCanvas && chartData.pieCategory.length > 0) {
        setTimeout(() => {
            const t = theme();
            pieCatInstance = new Chart(pieCatCanvas, {
                type: "doughnut",
                data: {
                    labels: chartData.pieCategory.map((d) => d.name),
                    datasets: [
                        {
                            data: chartData.pieCategory.map((d) => d.count),
                            backgroundColor: chartData.pieCategory.map(
                                (d) => lightenHex(d.color, t.pieCatLighten) + t.pieCatAlpha,
                            ),
                            borderColor: t.borderPie,
                            borderWidth: 2,
                        },
                    ],
                },
                options: {
                    animation: {
                        animateRotate: true,
                        animateScale: true,
                        duration: 1200,
                        easing: "easeOutQuart",
                    },
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { color: t.text, font: { size: 11 }, boxBorderColor: t.legendBoxBorder },
                        },
                    },
                },
            });
        }, 2000);
    }

    // ---- 円グラフ2: ユーザー投稿数 TOP5 ----
    // 2秒遅延でフェードイン完了後にアニメーション開始
    let pieUserInstance = null;
    const pieUserCanvas = document.getElementById("pieUser");
    if (pieUserCanvas && chartData.pieUser.length > 0) {
        setTimeout(() => {
            const t = theme();
            pieUserInstance = new Chart(pieUserCanvas, {
                type: "doughnut",
                data: {
                    labels: chartData.pieUser.map((d) => d.name),
                    datasets: [
                        {
                            data: chartData.pieUser.map((d) => d.count),
                            backgroundColor: t.pieUserColors.slice(
                                0,
                                chartData.pieUser.length,
                            ),
                            borderColor: t.borderPie,
                            borderWidth: 2,
                        },
                    ],
                },
                options: {
                    animation: {
                        animateRotate: true,
                        animateScale: true,
                        duration: 1200,
                        easing: "easeOutQuart",
                    },
                    plugins: {
                        legend: {
                            position: "bottom",
                            labels: { color: t.text, font: { size: 11 }, boxBorderColor: t.legendBoxBorder },
                        },
                    },
                },
            });
        }, 2000);
    }

    // ---- 棒グラフ: 翻訳価値スコア（SEO評価・技術性・構造品質・拡散適性・総合点） ----
    let barChartInstance = null;

    const renderBarChart = (data) => {
        if (barChartInstance) barChartInstance.destroy();

        const t = theme();

        // X軸 = 記事グループ(5件)、データセット = 翻訳評価5指標 + 平均値ライン
        const labels = data.map((d) => d.title);

        // 各指標を0-100スケールに正規化
        const seoScores       = data.map((d) => d.ai_score ? Math.round((d.ai_score.seo       || 0) / 40 * 100) : 0);
        const techScores      = data.map((d) => d.ai_score ? Math.round((d.ai_score.tech      || 0) / 25 * 100) : 0);
        const structureScores = data.map((d) => d.ai_score ? Math.round((d.ai_score.structure || 0) / 20 * 100) : 0);
        const spreadScores    = data.map((d) => d.ai_score ? Math.round((d.ai_score.spread    || 0) / 15 * 100) : 0);
        const totalScores     = data.map((d) => d.ai_score ? (d.ai_score.translate_score || 0) : 0);

        // 5指標の正規化値の平均（記事ごと）
        const avgScores = data.map((_, i) => {
            const vals = [seoScores[i], techScores[i], structureScores[i], spreadScores[i], totalScores[i]];
            return Math.round(vals.reduce((a, b) => a + b, 0) / vals.length);
        });

        // 指標名（バー下縦書きラベル用）3〜5文字
        const metricNames = ["SEO評価", "技術性", "構造品質", "拡散適性", "総合点"];

        // カスタムプラグイン: 各バー(25個)の直下に1文字ずつ縦積みで指標名を描画
        const barMetricLabelPlugin = {
            id: "barMetricLabel",
            afterDraw(chart) {
                const { ctx, chartArea } = chart;
                const fontSize = 9;
                const lineH = fontSize + 2;

                metricNames.forEach((name, dsIdx) => {
                    const meta = chart.getDatasetMeta(dsIdx);
                    if (meta.hidden) return;
                    meta.data.forEach((bar) => {
                        ctx.save();
                        ctx.font = `${fontSize}px sans-serif`;
                        ctx.fillStyle = t.text;
                        ctx.textAlign = "center";
                        ctx.textBaseline = "top";
                        [...name].forEach((char, ci) => {
                            ctx.fillText(char, bar.x, chartArea.bottom + 5 + ci * lineH);
                        });
                        ctx.restore();
                    });
                });
            },
        };

        barChartInstance = new Chart(barCanvas, {
            type: "bar",
            plugins: [barMetricLabelPlugin],
            data: {
                labels,
                datasets: [
                    {
                        label: "SEO評価",
                        data: seoScores,
                        backgroundColor: t.barColors[0],
                        pointStyle: "rect",
                    },
                    {
                        label: "技術性",
                        data: techScores,
                        backgroundColor: t.barColors[1],
                        pointStyle: "rect",
                    },
                    {
                        label: "構造品質",
                        data: structureScores,
                        backgroundColor: t.barColors[2],
                        pointStyle: "rect",
                    },
                    {
                        label: "拡散適性",
                        data: spreadScores,
                        backgroundColor: t.barColors[3],
                        pointStyle: "rect",
                    },
                    {
                        label: "総合点",
                        data: totalScores,
                        backgroundColor: t.barColors[4],
                        pointStyle: "rect",
                    },
                    {
                        type: "line",
                        label: "平均値",
                        data: avgScores,
                        borderColor: t.subText,
                        backgroundColor: t.subText,
                        pointBackgroundColor: t.subText,
                        pointStyle: "circle",
                        pointRadius: 4,
                        fill: false,
                        tension: 0.2,
                        order: 0,
                    },
                ],
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                layout: {
                    padding: { bottom: 55 }, // 「構造品質」4文字分の縦積み余白
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100,
                        ticks: { color: t.subText },
                        grid: { color: t.gridLine },
                    },
                    x: {
                        ticks: { display: false }, // 記事タイトルは非表示
                        grid: { display: false },
                    },
                },
                plugins: {
                    legend: {
                        labels: {
                            color: t.text,
                            font: { size: 11 },
                            usePointStyle: true,  // 各データセットの pointStyle を凡例に反映
                        },
                    },
                },
                animation: {
                    duration: 800,
                    easing: "easeOutQuart",
                    delay: (ctx) => {
                        const seed =
                            (ctx.dataIndex * 7 + ctx.datasetIndex * 13) % 25;
                        return seed * 60;
                    },
                },
            },
        });
    };

    // 初期描画: canvas を非表示にしてから描画（visibility はレイアウトに影響しない）
    // try/finally で必ず visible に戻す（モバイルでのエラー時に非表示固定になるのを防止）
    barCanvas.style.visibility = "hidden";
    requestAnimationFrame(() => {
        try {
            renderBarChart(chartData.bar);
        } finally {
            barCanvas.style.visibility = "visible";
        }
    });

    // ---- テーマ切替時に全チャートのカラーを即時更新 ----
    const updateChartsOnThemeChange = () => {
        const t = theme();

        if (pieCatInstance) {
            pieCatInstance.data.datasets[0].borderColor = t.borderPie;
            pieCatInstance.data.datasets[0].backgroundColor = chartData.pieCategory.map(
                (d) => lightenHex(d.color, t.pieCatLighten) + t.pieCatAlpha,
            );
            pieCatInstance.options.plugins.legend.labels.color = t.text;
            pieCatInstance.options.plugins.legend.labels.boxBorderColor = t.legendBoxBorder;
            pieCatInstance.update("none"); // アニメーションなしで即時反映
        }

        if (pieUserInstance) {
            pieUserInstance.data.datasets[0].borderColor = t.borderPie;
            pieUserInstance.data.datasets[0].backgroundColor = t.pieUserColors.slice(
                0,
                chartData.pieUser.length,
            );
            pieUserInstance.options.plugins.legend.labels.color = t.text;
            pieUserInstance.options.plugins.legend.labels.boxBorderColor = t.legendBoxBorder;
            pieUserInstance.update("none");
        }

        if (barChartInstance) {
            renderBarChart(chartData.bar);
        }
    };

    // data-bs-theme 属性の変更を監視して即時反映
    new MutationObserver(() => {
        updateChartsOnThemeChange();
    }).observe(document.documentElement, { attributes: true, attributeFilter: ["data-bs-theme"] });

    // ---- 解析ボタン ----
    const analyzeBtn = document.getElementById("analyzeBtn");
    const analyzeLoading = document.getElementById("analyzeLoading");
    const analyzeError = document.getElementById("analyzeError");

    if (analyzeBtn) {
        analyzeBtn.addEventListener("click", async () => {
            // AI有料機能の確認
            if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;

            analyzeBtn.disabled = true;
            analyzeLoading.classList.remove("d-none");
            analyzeError.classList.add("d-none");

            try {
                const csrfToken =
                    document.querySelector('input[name="csrf_token"]')
                        ?.value || "";
                const res = await fetch("/admin/analyze", {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrfToken,
                    },
                });

                if (!res.ok) throw new Error(`HTTP ${res.status}`);
                const json = await res.json();

                if (json.status === "ok") {
                    renderBarChart(json.data);
                    updateAdminPoints(json.remaining_points);
                } else {
                    throw new Error("API error");
                }
            } catch (e) {
                console.error("######## 解析エラー ########", e);
                analyzeError.classList.remove("d-none");
            } finally {
                analyzeBtn.disabled = false;
                analyzeLoading.classList.add("d-none");
            }
        });
    }
});

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

/* =========================
   固定ページ管理: AI生成・画像ランダム入れ替え
========================== */
(function () {
    // 削除確認
    document.querySelectorAll(".fixed-delete-form").forEach((form) => {
        form.addEventListener("submit", (e) => {
            if (!confirm("このページをDBから削除しますか？\n（テンプレートファイルは残ります）")) {
                e.preventDefault();
            }
        });
    });

    const genBtn = document.getElementById("fixed-gen-btn");
    if (!genBtn) return;

    // 画像プレビューを更新するヘルパー
    function setGenImage(filename) {
        document.getElementById("fixed-gen-img").src = "/static/images/fixed/" + filename;
        document.getElementById("fixed-gen-img-name").textContent = filename;
        document.getElementById("fc-image").value = filename;
    }

    // AI 生成ボタン
    genBtn.addEventListener("click", async () => {
        const title = document.getElementById("fixed-gen-title").value.trim();
        if (!title) {
            alert("タイトルを入力してください");
            return;
        }

        // AI有料機能の確認
        if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;

        document.getElementById("fixed-gen-loading").classList.remove("d-none");
        document.getElementById("fixed-gen-preview").classList.add("d-none");
        document.getElementById("fixed-gen-error").classList.add("d-none");
        genBtn.disabled = true;

        try {
            const resp = await fetch("/admin/fixed/generate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ title }),
            });
            const data = await resp.json();

            if (data.status !== "ok") {
                const errEl = document.getElementById("fixed-gen-error");
                errEl.textContent = data.message || "AI生成に失敗しました";
                errEl.classList.remove("d-none");
                return;
            }

            // プレビューに反映
            document.getElementById("fixed-gen-key").value = data.key;
            document.getElementById("fixed-gen-key-label").textContent = data.key;
            document.getElementById("fixed-gen-summary").value = data.summary;
            document.getElementById("fixed-gen-content-preview").textContent =
                data.content.substring(0, 500) + (data.content.length > 500 ? "…" : "");

            // hidden フィールドに格納
            document.getElementById("fc-key").value = data.key;
            document.getElementById("fc-title").value = title;
            document.getElementById("fc-summary").value = data.summary;
            document.getElementById("fc-content").value = data.content;
            setGenImage(data.image);

            document.getElementById("fixed-gen-preview").classList.remove("d-none");
            updateAdminPoints(data.remaining_points);
        } catch (err) {
            const errEl = document.getElementById("fixed-gen-error");
            errEl.textContent = "通信エラーが発生しました";
            errEl.classList.remove("d-none");
        } finally {
            document.getElementById("fixed-gen-loading").classList.add("d-none");
            genBtn.disabled = false;
        }
    });

    // 要約編集時に hidden フィールドも同期
    document.getElementById("fixed-gen-summary").addEventListener("input", () => {
        document.getElementById("fc-summary").value =
            document.getElementById("fixed-gen-summary").value;
    });

    // 画像入れ替えボタン
    document.getElementById("fixed-gen-swap-btn").addEventListener("click", async () => {
        const btn = document.getElementById("fixed-gen-swap-btn");
        btn.disabled = true;
        try {
            const resp = await fetch("/admin/fixed/random-image");
            const data = await resp.json();
            setGenImage(data.image);
        } catch (err) {
            console.error("画像取得エラー", err);
        } finally {
            btn.disabled = false;
        }
    });

    /* =========================
      固定ページ D&D 並び替え（Sortable.js）
    ========================== */
    function initFixedPageSortable(listId, toastId) {
        const el = document.getElementById(listId);
        if (!el || typeof Sortable === 'undefined') return;

        Sortable.create(el, {
            handle: '.fixed-drag-handle',
            animation: 150,
            ghostClass: 'sortable-ghost',
            onEnd: async () => {
                // 現在の並び順から id 配列を生成
                const ids = [...el.querySelectorAll('[data-page-id]')]
                    .map(node => parseInt(node.dataset.pageId, 10));

                try {
                    const resp = await fetch('/admin/fixed/reorder', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ ids }),
                    });
                    if (!resp.ok) throw new Error('reorder failed');

                    // 順序列の表示を更新
                    el.querySelectorAll('[data-page-id]').forEach((node, i) => {
                        const display = node.querySelector('.fixed-order-display');
                        if (display) display.textContent = i;
                    });

                    // 保存完了フィードバック
                    const toast = document.getElementById(toastId);
                    if (toast) {
                        toast.classList.remove('d-none');
                        clearTimeout(toast._hideTimer);
                        toast._hideTimer = setTimeout(() => toast.classList.add('d-none'), 2000);
                    }
                } catch (err) {
                    console.error('固定ページ並び替え保存エラー:', err);
                }
            },
        });
    }

    initFixedPageSortable('sortable-global-table',  'reorder-toast-global');
    initFixedPageSortable('sortable-footer-table',  'reorder-toast-footer');
    initFixedPageSortable('sortable-global-mobile', 'reorder-toast-global');
    initFixedPageSortable('sortable-footer-mobile', 'reorder-toast-footer');

})();

/* =========================
   マーケティング戦略ページ: AI翻訳ボタン
========================== */
(function () {
    document.querySelectorAll(".translate-btn").forEach((btn) => {
        btn.addEventListener("click", async () => {
            // AI有料機能の確認
            if (!confirm("この操作はGemini AI（有料）を使用します。\n実行しますか？")) return;

            const memoId = btn.dataset.memoId;
            const row = btn.closest("[data-memo-id]");
            const resultArea = document.getElementById("translate-result-" + memoId);
            const errorArea  = document.getElementById("translate-error-" + memoId);

            btn.disabled = true;
            btn.textContent = "翻訳中...";
            if (errorArea) errorArea.classList.add("d-none");

            const csrfToken = document.querySelector('input[name="csrf_token"]')?.value || "";

            try {
                const res = await fetch("/admin/translate/" + memoId, {
                    method: "POST",
                    headers: {
                        "X-Requested-With": "XMLHttpRequest",
                        "X-CSRFToken": csrfToken,
                    },
                });

                const json = await res.json();

                if (!res.ok || json.status !== "ok") {
                    throw new Error(json.message || `HTTP ${res.status}`);
                }

                // 翻訳結果を表示（アコーディオン展開）
                if (resultArea) {
                    const titleEl = resultArea.querySelector(".translate-title");
                    const bodyEl  = resultArea.querySelector(".translate-body");
                    if (titleEl) titleEl.textContent = json.translated_title;
                    if (bodyEl)  bodyEl.textContent  = json.translated_body;
                    resultArea.classList.remove("d-none");
                }

                // ボタンを「翻訳済み」表示に変更
                btn.textContent = "翻訳済み";
                btn.classList.add("opacity-75");
                updateAdminPoints(json.remaining_points);

            } catch (err) {
                console.error("######## AI翻訳エラー ########", err);
                if (errorArea) {
                    errorArea.textContent = err.message || "翻訳に失敗しました";
                    errorArea.classList.remove("d-none");
                }
                btn.disabled = false;
                btn.innerHTML = 'AI翻訳 <small class="ms-1 opacity-75" style="font-size:0.68em;font-weight:normal">有料</small>';
            }
        });
    });
})();

/* =========================
    一時停止希望 吹き出しフォーム（admin/index）
    テーブルのclip/z-index問題を回避するため、
    表示時に body 直下へ移動して position:fixed で配置する
========================== */
document.addEventListener("click", (e) => {
    // 「一時停止希望」ボタン：対応する吹き出しをトグル
    const triggerBtn = e.target.closest(".js-suspend-btn");
    if (triggerBtn) {
        e.stopPropagation();
        const userId = triggerBtn.dataset.userId;
        const popover = document.getElementById("suspend-popover-" + userId);
        if (!popover) return;

        // 他の吹き出しを全て閉じる
        document.querySelectorAll(".suspend-popover:not(.d-none)").forEach((p) => {
            if (p !== popover) p.classList.add("d-none");
        });

        if (popover.classList.contains("d-none")) {
            // ボタンの位置を取得して fixed 座標を算出
            const rect = triggerBtn.getBoundingClientRect();
            const left = Math.max(8, rect.right - 220);
            popover.style.top  = (rect.bottom + 8) + "px";
            popover.style.left = left + "px";
            // body 直下に移動してテーブルのスタッキングコンテキストから脱出
            document.body.appendChild(popover);
            popover.classList.remove("d-none");
        } else {
            popover.classList.add("d-none");
        }
        return;
    }
    // 「×（キャンセル）」ボタン
    const cancelBtn = e.target.closest(".js-suspend-cancel");
    if (cancelBtn) {
        cancelBtn.closest(".suspend-popover")?.classList.add("d-none");
        return;
    }
    // 吹き出し内クリックは伝播させない
    if (e.target.closest(".suspend-popover")) return;
    // 外クリックで全て閉じる
    document.querySelectorAll(".suspend-popover").forEach((p) => p.classList.add("d-none"));
});

// ユーザー属性帯グラフ: 左からバーが伸びるアニメーション
(function () {
    const firstTrack = document.querySelector(".attr-band-track");
    if (!firstTrack) return;

    const fills = document.querySelectorAll(".attr-band-fill");

    const animate = () => {
        fills.forEach((fill, i) => {
            const pct = fill.dataset.pct;
            fill.style.setProperty("--attr-target-pct", pct + "%");
            // 各セグメントをわずかに遅延させてリレー感を出す
            setTimeout(() => fill.classList.add("attr-animated"), i * 40);
        });
    };

    const observer = new IntersectionObserver(
        (entries) => {
            if (entries[0].isIntersecting) {
                animate();
                observer.disconnect();
            }
        },
        { threshold: 0.3 }
    );
    observer.observe(firstTrack);
})();

/* =========================
  テスト網羅率 実行ボタン
========================== */
(() => {
    const runBtn = document.getElementById('coverageRunBtn');
    if (!runBtn) return;

    const loading        = document.getElementById('coverageLoading');
    const emptyMsg       = document.getElementById('coverageEmpty');
    const result         = document.getElementById('coverageResult');
    const totalPct       = document.getElementById('totalPct');
    const covStmts       = document.getElementById('covStmts');
    const lastRun        = document.getElementById('lastRun');
    const totalBar       = document.getElementById('totalBar');
    const filesBadge     = document.getElementById('filesBadge');
    const funcBadge      = document.getElementById('funcBadge');
    const classBadge     = document.getElementById('classBadge');
    const tableBody      = document.getElementById('coverageTableBody');
    const funcTableBody  = document.getElementById('coverageFuncTableBody');
    const classTableBody = document.getElementById('coverageClassTableBody');
    const coverageSummary     = document.getElementById('coverageSummary');
    const coverageImprovement = document.getElementById('coverageImprovement');

    // 総合評価・改善ポイントのHTMLを生成する
    function buildEvaluation(cov) {
        const pct = cov.total_pct;

        // 総合評価
        let label, desc;
        if (pct >= 70) {
            label = '優良';
            desc  = 'カバレッジが目標(50%)を大幅に超えています。高い品質を維持できています。';
        } else if (pct >= 50) {
            label = '目標達成';
            desc  = 'カバレッジが目標(50%)を達成しています。引き続きテストを充実させましょう。';
        } else if (pct >= 40) {
            label = '普通';
            desc  = '目標の50%まであと一歩です。重要なモジュールから優先的にテストを追加しましょう。';
        } else {
            label = '要改善';
            desc  = 'カバレッジが目標(50%)を下回っています。未テストのファイルへの対応を優先してください。';
        }
        const summaryHtml = `<p class="fw-bold pt-2 me-2 badge rounded-pill text-bg-secondary" style="font-size:1.25rem;">${label}</p>
            <p class="text-body-secondary mb-0" style="font-size:1.2rem;">${desc}</p>`;

        // 改善ポイント
        const zeroFiles = cov.files.filter(f => f.pct === 0);
        const missFiles = cov.files.filter(f => f.missing > 0).sort((a, b) => b.missing - a.missing);
        let improvHtml = '';
        if (zeroFiles.length > 0) {
            const items = zeroFiles.slice(0, 3).map(f =>
                `<li class="font-monospace text-body-secondary" style="font-size:0.78rem;">${f.name}</li>`
            ).join('');
            const more  = zeroFiles.length > 3
                ? `<li class="text-body-secondary" style="font-size:0.78rem;">… 他 ${zeroFiles.length - 3} 件</li>` : '';
            improvHtml += `<p class="fw-semibold mb-1" style="font-size:1.2rem;"><i class="fa fa-circle-o me-1"></i>未テストファイル（${zeroFiles.length}件）</p>
                <ul class="list-unstyled mb-2 ps-2">${items}${more}</ul>`;
        }
        if (missFiles.length > 0) {
            const items = missFiles.slice(0, 3).map(f =>
                `<li class="font-monospace text-body-secondary" style="font-size:0.78rem;">${f.name}<span class="ms-1 fw-bold">${f.missing}</span><span class="ms-1 opacity-75" style="font-size:0.7rem;">行未カバー</span></li>`
            ).join('');
            improvHtml += `<p class="fw-semibold mb-1" style="font-size:1.2rem;"><i class="fa fa-exclamation-circle me-1"></i>未カバー行が多いファイル（上位3件）</p>
                <ul class="list-unstyled mb-0 ps-2">${items}</ul>`;
        }
        if (!zeroFiles.length && !missFiles.length) {
            improvHtml = '<p class="text-body-secondary mb-0" style="font-size:1.2rem;"><i class="fa fa-check me-1"></i>すべてのファイルがカバーされています。</p>';
        }
        return { summaryHtml, improvHtml };
    }

    // プログレスバー付きセルを生成する共通関数
    function pctCell(pct) {
        const opacity = pct < 40 ? ' opacity-50' : pct < 70 ? ' opacity-75' : '';
        return `<div class="d-flex align-items-center gap-2">
            <div class="progress flex-grow-1" style="height:14px;">
                <div class="progress-bar bg-secondary${opacity}" style="width:${pct}%;"></div>
            </div>
            <span style="width:42px;text-align:right;">${pct}%</span>
        </div>`;
    }

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
            totalPct.textContent     = cov.total_pct + '%';
            covStmts.innerHTML       = `<span class="fs-5">${cov.total_covered}</span> / ${cov.total_stmts} ステートメント`;
            lastRun.textContent      = '最終実行: ' + cov.last_run;
            totalBar.style.width     = cov.total_pct + '%';

            // 総合評価・改善ポイント更新
            const { summaryHtml, improvHtml } = buildEvaluation(cov);
            if (coverageSummary)     coverageSummary.innerHTML     = summaryHtml;
            if (coverageImprovement) coverageImprovement.innerHTML = improvHtml;

            filesBadge.textContent   = cov.files.length;
            funcBadge.textContent    = cov.functions.length;
            classBadge.textContent   = cov.classes.length;

            // グリッドヘッダー生成
            const filesHdr = `<div class="cov-row cov-hdr">
                <span class="cov-col-name">ファイル</span>
                <span class="cov-col-stmts">Stmts</span>
                <span class="cov-col-miss">Miss</span>
                <span class="cov-col-bar">カバレッジ</span>
            </div>`;
            const itemsHdr = (col1) => `<div class="cov-row cov-hdr">
                <span class="cov-col-name">${col1}</span>
                <span class="cov-col-file">ファイル</span>
                <span class="cov-col-stmts">Stmts</span>
                <span class="cov-col-miss">Miss</span>
                <span class="cov-col-bar">カバレッジ</span>
            </div>`;

            // ファイルグリッド再描画
            tableBody.innerHTML = filesHdr + cov.files.map(f => `
                <div class="cov-row">
                    <span class="cov-col-name font-monospace">${f.name}</span>
                    <span class="cov-col-stmts">${f.stmts}</span>
                    <span class="cov-col-miss text-body-secondary">${f.missing}</span>
                    <span class="cov-col-bar">${pctCell(f.pct)}</span>
                </div>`).join('');

            // 関数グリッド再描画
            funcTableBody.innerHTML = itemsHdr('関数 / メソッド') + cov.functions.map(f => `
                <div class="cov-row">
                    <span class="cov-col-name font-monospace fw-semibold">${f.name}</span>
                    <span class="cov-col-file text-body-secondary font-monospace">${f.file}:${f.line}</span>
                    <span class="cov-col-stmts">${f.stmts}</span>
                    <span class="cov-col-miss text-body-secondary">${f.missing}</span>
                    <span class="cov-col-bar">${pctCell(f.pct)}</span>
                </div>`).join('');

            // クラスグリッド再描画
            classTableBody.innerHTML = itemsHdr('クラス') + cov.classes.map(c => `
                <div class="cov-row">
                    <span class="cov-col-name font-monospace fw-semibold">${c.name}</span>
                    <span class="cov-col-file text-body-secondary font-monospace">${c.file}:${c.line}</span>
                    <span class="cov-col-stmts">${c.stmts}</span>
                    <span class="cov-col-miss text-body-secondary">${c.missing}</span>
                    <span class="cov-col-bar">${pctCell(c.pct)}</span>
                </div>`).join('');

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

                const level = btn.dataset.level || null; // ALL の場合は null
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

    // サービス構成図モーダル：描画後にコンテナ幅へスケール調整
    const serviceModal = document.getElementById('modal_service');
    if (serviceModal) {
        let serviceDrawioInitialized = false;

        function scaleServiceDrawio() {
            const mxDiv = serviceModal.querySelector('.mxgraph');
            if (!mxDiv) return;
            const inner = mxDiv.querySelector(':scope > div');
            if (!inner) return;
            const containerW = mxDiv.offsetWidth;
            const innerW = inner.scrollWidth;
            if (innerW > 0 && containerW > 0) {
                const scale = containerW / innerW;
                inner.style.transformOrigin = 'top left';
                inner.style.transform = 'scale(' + scale + ')';
                mxDiv.style.height = Math.round(inner.scrollHeight * scale) + 'px';
            }
        }

        serviceModal.addEventListener('shown.bs.modal', function () {
            if (window.GraphViewer && !serviceDrawioInitialized) {
                GraphViewer.processElements();
                serviceDrawioInitialized = true;
            }
            // mxGraph描画完了を待ってからスケール適用
            setTimeout(scaleServiceDrawio, 400);
        });
    }

})();
