import sys
import os

# Add the parent directory to sys.path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database import engine
from models import User
from security import hash_password
from sqlmodel import Session, select

def seed_admin():
    with Session(engine) as session:
        admin = session.exec(select(User).where(User.username == "admin")).first()
        if not admin:
            admin_user = User(
                full_name="System Admin",
                username="admin",
                email="admin@example.com",
                password_hash=hash_password("admin123"),
                role="admin",
                is_active=True
            )
            session.add(admin_user)
            session.commit()
            print("Successfully created admin user: username='admin', password='admin123'")
        else:
            print("Admin user already exists.")

if __name__ == "__main__":
    seed_admin()