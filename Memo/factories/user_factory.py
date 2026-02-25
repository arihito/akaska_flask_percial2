import os
import random
import factory
from factory.alchemy import SQLAlchemyModelFactory
from werkzeug.security import generate_password_hash

from models import User
from app import db

JAPANESE_LAST_NAMES = [
    "佐藤", "鈴木", "高橋", "田中", "伊藤", "渡辺", "山本", "中村", "小林",
    "加藤", "吉田", "山田", "佐々木", "山口", "松本", "井上", "木村", "林"
]

JAPANESE_FIRST_NAMES = [
    "太郎", "花子", "健", "愛", "翔", "美咲", "優", "結衣", "大輔", "彩"
]

NAMES = [
    last + first
    for last in JAPANESE_LAST_NAMES
    for first in JAPANESE_FIRST_NAMES
]


class UserFactory(SQLAlchemyModelFactory):
    class Meta:
        model = User
        sqlalchemy_session = db.session
        sqlalchemy_session_persistence = "flush"

    username = factory.Iterator(
        random.sample(NAMES, len(NAMES))
    )

    email = factory.Sequence(
        lambda n: f"user{n}@example.com"
    )

    password = factory.LazyFunction(
        lambda: generate_password_hash("pass1234%")
    )

    thumbnail = factory.Faker(
        "random_element",
        elements=[f"{i:03}.png" for i in range(1, 11)]
    )

    gender = factory.Faker(
        "random_element",
        elements=["男性", "女性"]
    )

    age_range = factory.Faker(
        "random_element",
        elements=["0〜10", "10〜20", "20〜30", "30〜40", "40〜50", "50〜60", "60以上"]
    )

    address = factory.Faker(
        "random_element",
        elements=["東京都", "神奈川県", "埼玉県", "千葉県", "その他"]
    )

    occupation = factory.Faker(
        "random_element",
        elements=["学生", "会社員", "自営業", "主婦・主夫", "その他"]
    )
