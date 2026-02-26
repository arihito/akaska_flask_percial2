import os
import csv
import subprocess
from flask import Blueprint, current_app, Response
from sqlalchemy import inspect
from collections import defaultdict
from datetime import datetime
try:
    from diagrams import Diagram, Cluster
    from diagrams.programming.framework import Flask as FlaskNode
    from diagrams.programming.language import Python
    from diagrams.onprem.client import Users
    DIAGRAMS_AVAILABLE = True
except ImportError:
    DIAGRAMS_AVAILABLE = False

docs_bp = Blueprint("docs", __name__)


@docs_bp.route("/diagram")
def diagram():
    if not DIAGRAMS_AVAILABLE:
        return Response(status=204)

    project_root = current_app.root_path
    output_dir = os.path.join(project_root, "static", "docs")
    os.makedirs(output_dir, exist_ok=True)

    filepath = os.path.join(output_dir, "architecture")

    routes_by_bp = defaultdict(list)

    for rule in current_app.url_map.iter_rules():
        if rule.endpoint == "static":
            continue

        if "." in rule.endpoint:
            bp_name, endpoint = rule.endpoint.split(".", 1)
        else:
            bp_name = "app"

        routes_by_bp[bp_name].append(str(rule))

    with Diagram(
        "Memo Dynamic Architecture",
        filename=filepath,
        show=False,
        direction="LR",
    ):

        user = Users("User")
        flask_core = FlaskNode("Flask App")
        user >> flask_core

        for bp_name, routes in routes_by_bp.items():
            with Cluster(f"Blueprint: {bp_name}"):
                bp_node = FlaskNode(bp_name)
                for route in routes:
                    route_node = Python(route)
                    bp_node >> route_node
            flask_core >> bp_node

    # 何も表示しない
    return Response(status=204)


@docs_bp.route("/generate-docs")
def generate_docs():

    project_root = current_app.root_path
    output_dir = os.path.join(project_root, "static", "docs")
    os.makedirs(output_dir, exist_ok=True)

    # ==========================
    # 1️⃣ ルーティング解析
    # ==========================
    routes = []
    for rule in current_app.url_map.iter_rules():

        if rule.endpoint == "static":
            continue

        routes.append({
            "endpoint": rule.endpoint,
            "url": str(rule),
            "methods": ",".join(sorted(rule.methods - {"HEAD", "OPTIONS"}))
        })

    # ==========================
    # 2️⃣ 機能定義書生成
    # ==========================
    function_path = os.path.join(output_dir, "function_spec.csv")
    with open(function_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["機能定義書"])
        writer.writerow([])
        writer.writerow(["業務", "機能名", "説明", "ランク"])

        for r in routes:
            if "POST" in r["methods"]:
                func = "登録"
                rank = "A"
            elif "DELETE" in r["methods"]:
                func = "削除"
                rank = "A"
            elif "PUT" in r["methods"] or "PATCH" in r["methods"]:
                func = "更新"
                rank = "A"
            else:
                func = "表示"
                rank = "B"

            writer.writerow([
                r["endpoint"].split(".")[0],
                func,
                f"{r['url']} の処理",
                rank
            ])

    # ==========================
    # 3️⃣ API定義書生成
    # ==========================
    api_path = os.path.join(output_dir, "api_spec.csv")
    with open(api_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["API定義書"])
        writer.writerow([])
        writer.writerow(["エンドポイント", "URL", "HTTPメソッド"])

        for r in routes:
            writer.writerow([r["endpoint"], r["url"], r["methods"]])

    # ==========================
    # 4️⃣ ルーティング一覧
    # ==========================
    route_path = os.path.join(output_dir, "route_list.csv")
    with open(route_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.writer(f)
        writer.writerow(["ルーティング一覧"])
        writer.writerow([])
        writer.writerow(["エンドポイント", "URL", "HTTPメソッド"])

        for r in routes:
            writer.writerow([r["endpoint"], r["url"], r["methods"]])

    # ==========================
    # 5️⃣ テーブル定義書生成
    # ==========================
    table_path = os.path.join(output_dir, "table_spec.csv")

    try:
        from app import db  # あなたのプロジェクトに合わせて調整
        inspector = inspect(db.engine)

        with open(table_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["テーブル定義書"])
            writer.writerow([])
            writer.writerow(["テーブル名", "カラム名", "型", "Nullable", "PK"])

            for table_name in inspector.get_table_names():
                columns = inspector.get_columns(table_name)
                for col in columns:
                    writer.writerow([
                        table_name,
                        col["name"],
                        str(col["type"]),
                        col["nullable"],
                        col.get("primary_key", False)
                    ])

    except Exception as e:
        with open(table_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["DB取得失敗", str(e)])

    # ==========================
    # 6️⃣ Git進行表生成
    # ==========================
    git_path = os.path.join(output_dir, "git_progress.csv")

    try:
        result = subprocess.run(
            ["git", "log", "--pretty=format:%h,%an,%ad,%s", "--date=short"],
            cwd=project_root,
            capture_output=True,
            text=True
        )

        lines = result.stdout.split("\n")

        with open(git_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Git進行表"])
            writer.writerow([])
            writer.writerow(["コミットID", "作成者", "日付", "メッセージ"])

            for line in lines:
                if line.strip():
                    writer.writerow(line.split(",", 3))

    except Exception as e:
        with open(git_path, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["Git取得失敗", str(e)])

    # 画面遷移しない
    return Response(status=204)

