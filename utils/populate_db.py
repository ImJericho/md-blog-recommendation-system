import json
import random
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models.database import Base, engine, User, Blog, BlogMetrics, BlogSimilarity, user_history, SessionLocal

def create_sample_users(db: Session, count: int = 10):
    """Create sample users with different streams and classes"""
    streams = ["Science", "Commerce", "Arts"]
    classes = ["11th", "12th"]
    
    for i in range(1, count + 1):
        user = User(
            user_id=i,
            name=f"User {i}",
            stream=random.choice(streams),
            class_name=random.choice(classes)
        )
        db.add(user)
    db.commit()

def create_sample_blogs(db: Session, count: int = 20):
    """Create sample blogs with random content"""
    tags = ["Mathematics", "Physics", "Chemistry", "Biology", "Economics", "History", "Geography"]
    exams = ["JEE", "NEET", "UPSC", "CA", "CBSE"]
    
    for i in range(1, count + 1):
        blog = Blog(
            blog_id=i,
            title=f"Sample Blog {i}",
            content=f"This is the content of sample blog {i}. It contains some random text for testing purposes.",
            tags=json.dumps(random.sample(tags, random.randint(1, 3))),
            exams=json.dumps(random.sample(exams, random.randint(1, 2))),
            read_time=random.randint(5, 30),
            conclusion=f"This is the conclusion of sample blog {i}.",
            creation_date=datetime.utcnow() - timedelta(days=random.randint(0, 365))
        )
        db.add(blog)
        
        # Create corresponding metrics
        metrics = BlogMetrics(
            blog_id=i,
            likes=random.randint(0, 100),
            views=random.randint(100, 1000)
        )
        db.add(metrics)
    db.commit()

def create_sample_user_history(db: Session):
    """Create sample user reading history"""
    users = db.query(User).all()
    blogs = db.query(Blog).all()
    
    for user in users:
        # Each user reads 3-7 random blogs
        read_count = random.randint(3, 7)
        read_blogs = random.sample(blogs, read_count)
        
        for blog in read_blogs:
            # Add to user history
            db.execute(
                user_history.insert().values(
                    user_id=user.user_id,
                    blog_id=blog.blog_id,
                    read_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
            )
    db.commit()

def create_sample_similarities(db: Session):
    """Create sample similarity scores between blogs"""
    blogs = db.query(Blog).all()
    
    for i, blog1 in enumerate(blogs):
        for blog2 in blogs[i+1:]:
            similarity = BlogSimilarity(
                blog_id_1=blog1.blog_id,
                blog_id_2=blog2.blog_id,
                similarity_score=random.uniform(0.1, 0.9)
            )
            db.add(similarity)
    db.commit()

def populate_database():
    """Main function to populate the database with sample data"""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    # Create a new session
    db = SessionLocal()
    
    try:
        # Create sample data
        create_sample_users(db)
        # create_sample_blogs(db)
        # create_sample_user_history(db)
        # create_sample_similarities(db)
        
        print("Database populated successfully!")
    except Exception as e:
        print(f"Error populating database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_database() 