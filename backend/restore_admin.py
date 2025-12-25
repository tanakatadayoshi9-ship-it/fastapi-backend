from app.database import SessionLocal
from app.models import User
from app.auth import hash_password

db = SessionLocal()

user = db.query(User).filter(User.username == "admin").first()

if not user:
    user = User(
        username="admin",
        hashed_password=hash_password("admin123"),
        role="admin"
    )
    db.add(user)
    db.commit()
    print("admin recreated")
else:
    user.role = "admin"
    db.commit()
    print("admin role restored")

db.close()

