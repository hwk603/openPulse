#!/usr/bin/env python3
"""
Reset OpenPulse database - WARNING: This will delete all data!
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal, engine, Base
from src.models.database import (
    RepositoryModel,
    ContributorModel,
    HealthScoreModel,
    ChurnPredictionModel,
    AnalysisTaskModel
)


def reset_database():
    """Drop all tables and recreate them"""
    print("⚠️  WARNING: This will delete ALL data from the database!")
    print("")
    response = input("Are you sure you want to continue? Type 'yes' to confirm: ")

    if response.lower() != "yes":
        print("❌ Database reset cancelled")
        return

    print("")
    print("🗑️  Dropping all tables...")

    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        print("✅ All tables dropped")

        # Recreate all tables
        print("🔨 Creating tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created")

        print("")
        print("🎉 Database reset completed successfully!")
        print("")
        print("The database is now empty. You can:")
        print("  1. Seed test data: python scripts/seed-data.py")
        print("  2. Start collecting real data via the API")

    except Exception as e:
        print(f"❌ Error during database reset: {e}")
        raise


if __name__ == "__main__":
    reset_database()
