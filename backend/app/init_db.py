"""Utility script to initialize database tables directly from the command line.

Usage:
    python -m app.init_db
"""
from app.database import init_db

if __name__ == "__main__":
    print("Creating all database tables...")
    init_db()
    print("Database tables created successfully!")
