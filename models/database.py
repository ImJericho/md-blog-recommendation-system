from sqlalchemy import Column, Integer, String, DateTime, Float, ForeignKey, Table, JSON, create_engine
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import os

Base = declarative_base()

# Database configuration - Using SQLite
DATABASE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'data')
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = f"sqlite:///{os.path.join('data', 'blog_recommender.db')}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Association table for user history
user_history = Table(
    'user_history',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.user_id')),
    Column('blog_id', Integer, ForeignKey('blogs.blog_id')),
    Column('read_at', DateTime, default=datetime.utcnow)
)

class User(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    stream = Column(String(50), nullable=False)
    class_name = Column(String(50), nullable=False)
    
    # Relationship with history
    read_history = relationship("Blog", secondary=user_history, back_populates="readers")

class Blog(Base):
    __tablename__ = 'blogs'
    
    blog_id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    content = Column(String, nullable=False)
    tags = Column(JSON, nullable=False)
    exams = Column(JSON, nullable=False)
    read_time = Column(Integer, nullable=False)
    conclusion = Column(String, nullable=False)
    creation_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationship with history
    readers = relationship("User", secondary=user_history, back_populates="read_history")
    
    # Relationship with dynamic metrics
    metrics = relationship("BlogMetrics", back_populates="blog", uselist=False)

class BlogMetrics(Base):
    __tablename__ = 'blog_metrics'
    
    blog_id = Column(Integer, ForeignKey('blogs.blog_id'), primary_key=True)
    likes = Column(Integer, default=0)
    views = Column(Integer, default=0)
    
    # Relationship with blog
    blog = relationship("Blog", back_populates="metrics")

# Table for storing similarity scores between blogs
class BlogSimilarity(Base):
    __tablename__ = 'blog_similarities'
    
    blog_id_1 = Column(Integer, ForeignKey('blogs.blog_id'), primary_key=True)
    blog_id_2 = Column(Integer, ForeignKey('blogs.blog_id'), primary_key=True)
    similarity_score = Column(Float, nullable=False) 