const { useEffect, useState } = React;

const ALLOWED_CHAR = /^[ぁ-んァ-ヶー一-龯a-zA-Z0-9_\-\.]+$/;

function UsernameStatus() {
    const [status, setStatus] = useState(null);
    const [message, setMessage] = useState(null);

    useEffect(() => {
        const input = document.getElementById("username");
        if (!input) return;

        let timer = null;

        const handler = (e) => {
            const value = e.target.value;

            // 文字数チェック（即時）
            if (value.length < 3 || value.length > 12) {
                setStatus(null);
                setMessage("ユーザー名は3〜12文字で入力してください");
                return;
            }

            // 不正文字チェック（1文字単位）
            if (!ALLOWED_CHAR.test(value)) {
                setStatus(null);
                setMessage("使用できない文字が含まれています");
                return;
            }

            setMessage(null);

            if (timer) clearTimeout(timer);

            timer = setTimeout(async () => {
                try {
                    const res = await fetch(
                        `/auth/api/check_userid?value=${encodeURIComponent(value)}`,
                        { credentials: "same-origin" }
                    );
                    setStatus(await res.json());
                } catch {
                    setStatus({ error: true });
                }
            }, 300);
        };

        input.addEventListener("input", handler);
        return () => input.removeEventListener("input", handler);
    }, []);
    return (
        <div className="mt-2 small">
            {message && <div className="alert alert-warning text-warning mt-3"><i className="fa fa-exclamation-triangle"></i>{message}</div>}
            {status?.available && <div className="alert alert-success text-success mt-3"><i className="fa fa-check-circle"></i>使用可能なユーザー名です</div>}
            {status?.exists && <div className="alert alert-danger text-danger mt-3"><i className="fa fa-user-times"></i>そのユーザー名は既に使用されています</div>}
            {status?.invalid_char && <div className="alert alert-warning text-warning mt-3"><i className="fa fa-exclamation-triangle"></i>使用できない文字が含まれています</div>}
            {status?.length_error && <div className="alert alert-warning text-warning mt-3"><i className="fa fa-exclamation-triangle"></i>3〜12文字で入力してください</div>}
            {status?.error && <div className="alert alert-danger text-danger mt-3"><i className="fa fa-times-circle-o"></i>意図しない通信エラーです</div>}
        </div>
    );
}
ReactDOM.createRoot(
    document.getElementById("username-status")
).render(<UsernameStatus />);