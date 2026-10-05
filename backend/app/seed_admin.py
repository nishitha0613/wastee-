"""Dedicated script to safely initialize or seed an administrator account.

Usage:
    python -m app.seed_admin

Environment Variables Used (from .env or process environment):
    ADMIN_NAME (default: "System Administrator")
    ADMIN_EMAIL (default: "admin@ecocycle.com")
    ADMIN_PASSWORD (default: "Admin@Secure123!")
"""
import sys
from app.config import get_settings
from app.database import SessionLocal, init_db
from app.models.user import User, UserRole
from app.utils.security import get_password_hash


def seed_admin() -> None:
    settings = get_settings()

    admin_name = settings.ADMIN_NAME
    admin_email = settings.ADMIN_EMAIL.strip().lower()
    admin_password = settings.ADMIN_PASSWORD

    if not admin_password or len(admin_password) < 6:
        print("[ERROR] ADMIN_PASSWORD must be at least 6 characters long.")
        sys.exit(1)

    # Ensure tables exist
    init_db()

    db = SessionLocal()
    try:
        existing_user = db.query(User).filter(User.email == admin_email).first()
        if existing_user:
            if existing_user.role == UserRole.ADMIN.value:
                print(f"[INFO] Admin account '{admin_email}' already exists. No changes made.")
            else:
                print(f"[WARNING] User '{admin_email}' exists but has role '{existing_user.role}'. Upgrading to admin...")
                existing_user.role = UserRole.ADMIN.value
                db.commit()
                print(f"[SUCCESS] User '{admin_email}' promoted to admin.")
            return

        # Hash the password securely
        password_hash = get_password_hash(admin_password)

        admin = User(
            name=admin_name,
            email=admin_email,
            password_hash=password_hash,
            role=UserRole.ADMIN.value,
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)

        print("[SUCCESS] Administrator account created successfully:")
        print(f"  ID:    {admin.id}")
        print(f"  Name:  {admin.name}")
        print(f"  Email: {admin.email}")
        print(f"  Role:  {admin.role}")
        print("  (Password hash stored securely via bcrypt)")

    finally:
        db.close()


if __name__ == "__main__":
    seed_admin()
