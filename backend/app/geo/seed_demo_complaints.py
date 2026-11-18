"""
Demo complaint seeder script for CivicWatch.

Inserts ~40 demo complaints around Noida (28.62, 77.36) with 3 dense clusters
and scattered points. The demo needs dense data to show clusters, heatmap,
and repeat-issue hotspots during viva presentations.
"""
import random
from backend.app.platform.database import SessionLocal
from backend.app.platform.models import User, Category, Complaint
from backend.app.platform.security import hash_password


def seed_demo_complaints():
    """
    Seed ~40 demo complaints in the Noida region if fewer than 20 demo complaints exist.
    """
    # Open database session
    db = SessionLocal()
    try:
        # Check if 20 or more demo complaints already exist to avoid duplicate seeding
        existing_demo_count = (
            db.query(Complaint)
            .filter(Complaint.title.like("Demo:%"))
            .count()
        )
        if existing_demo_count >= 20:
            print(f"Skipping seed: {existing_demo_count} demo complaints already exist.")
            return

        # Ensure at least one citizen user exists as owner
        user = db.query(User).first()
        if not user:
            user = User(
                name="Demo Citizen",
                email="demo_citizen@civicwatch.com",
                password_hash=hash_password("DemoPassword123!"),
                role="citizen",
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        # Ensure standard categories exist
        category_names = ["Pothole", "Garbage", "Water Leakage", "Streetlight"]
        categories = []
        for name in category_names:
            cat = db.query(Category).filter(Category.name == name).first()
            if not cat:
                cat = Category(name=name)
                db.add(cat)
                db.commit()
                db.refresh(cat)
            categories.append(cat)

        statuses = ["Submitted", "Under Review", "Assigned", "In Progress", "Resolved"]
        priorities = ["Low", "Medium", "High", "Critical"]

        # Define 3 dense cluster centres around Noida
        # Cluster 1: Sector 18 Commercial Hub (28.570, 77.322)
        # Cluster 2: Sector 62 IT Hub (28.628, 77.365)
        # Cluster 3: Sector 137 Expressway (28.513, 77.408)
        cluster_centers = [
            (28.570, 77.322, 10, "Sector 18 Hub"),
            (28.628, 77.365, 14, "Sector 62 IT Zone"),
            (28.513, 77.408, 10, "Sector 137 Residential"),
        ]

        complaints_to_add = []
        count = 1

        # Generate complaints for dense clusters
        for center_lat, center_lon, num_points, cluster_name in cluster_centers:
            for _ in range(num_points):
                # Add small random offset (~100-300m)
                offset_lat = random.uniform(-0.002, 0.002)
                offset_lon = random.uniform(-0.002, 0.002)
                cat = random.choice(categories)
                complaints_to_add.append(
                    Complaint(
                        title=f"Demo: {cat.name} in {cluster_name} #{count}",
                        description=f"Auto-generated demo issue reported near {cluster_name}.",
                        category_id=cat.id,
                        status=random.choice(statuses),
                        priority=random.choice(priorities),
                        latitude=round(center_lat + offset_lat, 6),
                        longitude=round(center_lon + offset_lon, 6),
                        user_id=user.id,
                    )
                )
                count += 1

        # Generate scattered complaints across greater Noida area (~6 points)
        for _ in range(6):
            scatter_lat = 28.62 + random.uniform(-0.08, 0.08)
            scatter_lon = 77.36 + random.uniform(-0.08, 0.08)
            cat = random.choice(categories)
            complaints_to_add.append(
                Complaint(
                    title=f"Demo: Scattered {cat.name} #{count}",
                    description="Scattered issue across Noida demo area.",
                    category_id=cat.id,
                    status=random.choice(statuses),
                    priority=random.choice(priorities),
                    latitude=round(scatter_lat, 6),
                    longitude=round(scatter_lon, 6),
                    user_id=user.id,
                )
            )
            count += 1

        # Save all generated complaints to database
        db.add_all(complaints_to_add)
        db.commit()
        print(f"Successfully seeded {len(complaints_to_add)} demo complaints.")

    finally:
        db.close()


if __name__ == "__main__":
    seed_demo_complaints()
