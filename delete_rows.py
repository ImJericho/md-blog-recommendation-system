from sqlalchemy.orm import Session
from sqlalchemy import text
from database import SessionLocal, engine
from models import User, UserActivity, Base

# Create the database tables
Base.metadata.create_all(bind=engine)

# Open a new session
db: Session = SessionLocal()

# Delete all user activities first to avoid foreign key constraint violations
db.query(UserActivity).delete()
db.commit()

# Delete all users
db.query(User).delete()
db.commit()

# Reset the auto-incrementing sequence for both users and user_activity tables
db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
db.execute(text("ALTER SEQUENCE user_activity_id_seq RESTART WITH 1;"))
db.commit()