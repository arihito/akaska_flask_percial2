import random

GITHUB_COLORS = [
    "#B60205", "#D93F0B", "#FBCA04",
    "#0E8A16", "#006B75", "#1D76DB",
    "#0052CC", "#5319E7"
]

def create_category(name):
    from app import db
    from app.models import Category

    color = random.choice(GITHUB_COLORS)

    category = Category(
        name=name[:12],  # 念のため
        color=color
    )

    db.session.add(category)
    db.session.commit()

    return category