from sqlalchemy.orm import sessionmaker
from recommendation import recommend
from models import Base, User, UserActivity
from database import SessionLocal

# Connect to the DB
db = SessionLocal()

# Ensure test user exists
if not db.query(User).filter(User.id == 1).first():
    test_user = User(
        email="testuser@example.com",
        name="Test User",
        phone="9999999999",
        classes="12",
        stream="Science",
        exam_interest="JEE"  # Make sure this field exists in your model
    )
    db.add(test_user)
    db.commit()
else:
    print("✅ Test user 1 already exists.\n")

# Blog to test
user_id = 1
blog_title = "How to prepare for JEE at this stage"

# Call the recommender
print(f"🔍 Requesting recommendations for blog: '{blog_title}'...")

try:
    results = recommend(user_id, blog_title, db)

    print("✅ Recommendations:\n")
    for i, blog in enumerate(results, 1):
        print(f"{i}. {blog['title']} — Tags: {blog['tags']} — Score: {blog['score']}")
except Exception as e:
    print(f"❌ Error during recommendation: {e}")

# Clean up
db.close()
