from sqlalchemy.orm import Session
from database import SessionLocal, engine, Base
from models import User, UserActivity

# Open a new session
db: Session = SessionLocal()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Add dummy users
users = [
    User(email="user1@example.com", name="User One", phone="1234567890", classes="10", stream="Science"),
    User(email="user2@example.com", name="User Two", phone="0987654321", classes="12", stream="Commerce"),
    User(email="user3@example.com", name="A", phone="1234567845", classes="10", stream="Science"),
    User(email="user4@example.com", name="B", phone="0987654323", classes="12", stream="Science"),
    User(email="user5@example.com", name="C", phone="1234567658", classes="10", stream="Science"),
    User(email="user6@example.com", name="D", phone="0987654589", classes="12", stream="Science")
]

for user in users:
    db.add(user)
db.commit()

# Add dummy user activities
activities = [
    UserActivity(user_id=1, blog_id=1),
    UserActivity(user_id=1, blog_id=2),
    UserActivity(user_id=3, blog_id=3),
    UserActivity(user_id=4, blog_id=4),
    UserActivity(user_id=5, blog_id=6),
    UserActivity(user_id=6, blog_id=8)
]

for activity in activities:
    db.add(activity)
db.commit()


# Close the session
db.close()

