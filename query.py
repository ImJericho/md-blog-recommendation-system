from sqlalchemy.orm import Session
from database import SessionLocal
from models import User, UserActivity

# Open a new session
db: Session = SessionLocal()

# Query the users table
users = db.query(User).all()
print("Users:")
for user in users:
    print(user.id, user.email, user.name, user.phone, user.classes, user.stream, user.created_at)

# Query the user_activity table
activities = db.query(UserActivity).all()
print("\nUser Activities:")
for activity in activities:
    print(activity.id, activity.user_id, activity.blog_id, activity.interaction_time)

# Close the session
db.close()
