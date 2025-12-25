from app.database import SessionLocal
from app.models import User

db = SessionLocal()

user = db.query(User).filter(User.username == "admin").first()
if not user:
    print("admin not found")
else:
    user.role = "admin"
    db.commit()
    print("admin role forced")

db.close()
