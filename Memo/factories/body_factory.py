import os
import random
from pathlib import Path


class BodyFactory:
    """Markdown形式の記事本文を提供するファクトリー"""

    # プロジェクトルートからの相対パスでarticlesディレクトリを指定
    ARTICLES_DIR = Path(__file__).parent.parent / "data" / "sample_articles"

    # カテゴリーごとのファイルマッピング
    CATEGORIES = {
        "basic": ["basic_001.md", "basic_002.md"],
        "crud": ["crud_001.md", "crud_002.md"],
        "ui": ["ui_001.md", "ui_002.md"],
        "auth": ["auth_001.md"],
        "package": ["package_001.md"],
        "api": ["api_001.md", "api_002.md"],
        "testing": ["testing_001.md"],
        "deploy": ["deploy_001.md"],
        "celery": ["celery_001.md"],
        "docker": ["docker_001.md"],
        "logging": ["logging_001.md"],
    }

    @classmethod
    def get_body(cls, category=None):
        """
        カテゴリーに応じた記事本文を取得

        Args:
            category (str): カテゴリー名（None の場合は全カテゴリーからランダム）

        Returns:
            str: Markdown形式の記事本文
        """
        if category and category in cls.CATEGORIES:
            files = cls.CATEGORIES[category]
        else:
            # 全カテゴリーからランダム選択
            files = [f for files in cls.CATEGORIES.values() for f in files]

        filename = random.choice(files)
        filepath = cls.ARTICLES_DIR / filename

        if not filepath.exists():
            raise FileNotFoundError(f"記事ファイルが見つかりません: {filepath}")

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    @classmethod
    def get_all_bodies(cls):
        """
        全記事本文をリストで返す

        Returns:
            list: 全記事本文のリスト
        """
        bodies = []
        for files in cls.CATEGORIES.values():
            for filename in files:
                filepath = cls.ARTICLES_DIR / filename
                if filepath.exists():
                    with open(filepath, "r", encoding="utf-8") as f:
                        bodies.append(f.read())
        return bodies

    @classmethod
    def get_body_by_index(cls, index):
        """
        インデックス指定で記事本文を取得（seed.py用）

        Args:
            index (int): 記事のインデックス

        Returns:
            str: Markdown形式の記事本文
        """
        all_files = [f for files in cls.CATEGORIES.values() for f in files]
        if index >= len(all_files):
            # インデックスが範囲外の場合はループさせる
            index = index % len(all_files)

        filename = all_files[index]
        filepath = cls.ARTICLES_DIR / filename

        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()
