#!/usr/bin/env python3
"""
Seed test data into OpenPulse database
"""

import sys
import os
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.database import SessionLocal
from src.models.database import (
    RepositoryModel,
    ContributorModel,
    HealthScoreModel,
    ChurnPredictionModel
)

# Sample repositories
SAMPLE_REPOS = [
    {"platform": "github", "owner": "apache", "repo": "iotdb"},
    {"platform": "github", "owner": "apache", "repo": "kafka"},
    {"platform": "github", "owner": "kubernetes", "repo": "kubernetes"},
    {"platform": "github", "owner": "facebook", "repo": "react"},
    {"platform": "github", "owner": "microsoft", "repo": "vscode"},
    {"platform": "github", "owner": "pytorch", "repo": "pytorch"},
    {"platform": "github", "owner": "tensorflow", "repo": "tensorflow"},
    {"platform": "github", "owner": "rust-lang", "repo": "rust"},
    {"platform": "github", "owner": "golang", "repo": "go"},
    {"platform": "github", "owner": "python", "repo": "cpython"},
]

# Sample contributors
SAMPLE_CONTRIBUTORS = [
    "alice", "bob", "charlie", "david", "eve",
    "frank", "grace", "henry", "iris", "jack"
]


def seed_repositories(db):
    """Seed sample repositories"""
    print("📦 Seeding repositories...")

    repos = []
    for repo_data in SAMPLE_REPOS:
        repo = RepositoryModel(
            platform=repo_data["platform"],
            owner=repo_data["owner"],
            repo=repo_data["repo"],
            full_name=f"{repo_data['owner']}/{repo_data['repo']}",
            description=f"Sample repository: {repo_data['owner']}/{repo_data['repo']}",
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(30, 365))
        )
        db.add(repo)
        repos.append(repo)

    db.commit()
    print(f"✅ Created {len(repos)} repositories")
    return repos


def seed_contributors(db, repos):
    """Seed sample contributors"""
    print("👥 Seeding contributors...")

    contributors = []
    for repo in repos:
        # Add 5-10 contributors per repository
        num_contributors = random.randint(5, 10)
        selected_contributors = random.sample(SAMPLE_CONTRIBUTORS, num_contributors)

        for username in selected_contributors:
            contributor = ContributorModel(
                platform=repo.platform,
                username=username,
                email=f"{username}@example.com",
                name=username.capitalize(),
                repository_id=repo.id,
                first_contribution_at=datetime.utcnow() - timedelta(days=random.randint(30, 365)),
                last_contribution_at=datetime.utcnow() - timedelta(days=random.randint(0, 30)),
                total_contributions=random.randint(10, 500),
                is_core_contributor=random.choice([True, False])
            )
            db.add(contributor)
            contributors.append(contributor)

    db.commit()
    print(f"✅ Created {len(contributors)} contributors")
    return contributors


def seed_health_scores(db, repos):
    """Seed sample health scores"""
    print("📊 Seeding health scores...")

    scores = []
    for repo in repos:
        # Create health scores for the last 30 days
        for days_ago in range(30, 0, -1):
            score = HealthScoreModel(
                repository_id=repo.id,
                overall_score=random.uniform(60.0, 95.0),
                activity_score=random.uniform(60.0, 95.0),
                diversity_score=random.uniform(60.0, 95.0),
                response_time_score=random.uniform(60.0, 95.0),
                code_quality_score=random.uniform(60.0, 95.0),
                documentation_score=random.uniform(60.0, 95.0),
                community_atmosphere_score=random.uniform(60.0, 95.0),
                lifecycle_stage=random.choice(["embryonic", "growth", "mature", "decline"]),
                analyzed_at=datetime.utcnow() - timedelta(days=days_ago)
            )
            db.add(score)
            scores.append(score)

    db.commit()
    print(f"✅ Created {len(scores)} health scores")
    return scores


def seed_churn_predictions(db, contributors):
    """Seed sample churn predictions"""
    print("⚠️  Seeding churn predictions...")

    predictions = []
    for contributor in contributors:
        prediction = ChurnPredictionModel(
            contributor_id=contributor.id,
            repository_id=contributor.repository_id,
            churn_risk_score=random.uniform(0.0, 100.0),
            risk_level=random.choice(["green", "yellow", "orange", "red"]),
            behavioral_decay_score=random.uniform(0.0, 100.0),
            network_marginalization_score=random.uniform(0.0, 100.0),
            temporal_anomaly_score=random.uniform(0.0, 100.0),
            community_engagement_score=random.uniform(0.0, 100.0),
            churn_probability_1m=random.uniform(0.0, 0.5),
            churn_probability_3m=random.uniform(0.0, 0.7),
            churn_probability_6m=random.uniform(0.0, 0.9),
            analyzed_at=datetime.utcnow()
        )
        db.add(prediction)
        predictions.append(prediction)

    db.commit()
    print(f"✅ Created {len(predictions)} churn predictions")
    return predictions


def main():
    """Main seeding function"""
    print("🌱 Starting database seeding...")
    print("")

    db = SessionLocal()

    try:
        # Check if data already exists
        existing_repos = db.query(RepositoryModel).count()
        if existing_repos > 0:
            print(f"⚠️  Database already contains {existing_repos} repositories")
            response = input("Do you want to clear existing data and reseed? (yes/no): ")
            if response.lower() != "yes":
                print("❌ Seeding cancelled")
                return

            # Clear existing data
            print("🧹 Clearing existing data...")
            db.query(ChurnPredictionModel).delete()
            db.query(HealthScoreModel).delete()
            db.query(ContributorModel).delete()
            db.query(RepositoryModel).delete()
            db.commit()
            print("✅ Existing data cleared")
            print("")

        # Seed data
        repos = seed_repositories(db)
        contributors = seed_contributors(db, repos)
        health_scores = seed_health_scores(db, repos)
        churn_predictions = seed_churn_predictions(db, contributors)

        print("")
        print("🎉 Database seeding completed successfully!")
        print("")
        print("Summary:")
        print(f"  📦 Repositories: {len(repos)}")
        print(f"  👥 Contributors: {len(contributors)}")
        print(f"  📊 Health Scores: {len(health_scores)}")
        print(f"  ⚠️  Churn Predictions: {len(churn_predictions)}")
        print("")
        print("You can now:")
        print("  1. Start the API: uvicorn src.api.main:app --reload")
        print("  2. Visit: http://localhost:8000/docs")
        print("  3. Try: GET /api/v1/repositories")

    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    main()
