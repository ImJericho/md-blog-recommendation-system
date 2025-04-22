from sqlalchemy import Column, Integer, String, TIMESTAMP, ForeignKey
from sqlalchemy.sql.expression import text
from sqlalchemy.orm import relationship
from database import Base
from pydantic import BaseModel

# SQLAlchemy Models

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    email = Column(String(100), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    phone = Column(String(13), unique=True, nullable=False)
    classes = Column(String(5), nullable=False)
    stream = Column(String(50), nullable=False)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationship to UserActivity
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")

class UserActivity(Base):
    __tablename__ = "user_activity"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    blog_id = Column(Integer, nullable=False)
    interaction_time = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

    # Relationship back to User
    user = relationship("User", back_populates="activities")

# Pydantic Models (if needed for FastAPI or other purposes)

class BlogRequest(BaseModel):
    user_id: int
    title: str

class NewBlogRequest(BaseModel):
    title: str
    description: str

class UserInteractionRequest(BaseModel):
    user_id: int
    blog_id: int


