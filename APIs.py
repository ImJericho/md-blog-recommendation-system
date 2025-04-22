from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import BlogRequest, NewBlogRequest, UserInteractionRequest, UserActivity, User, Base
from recommendation import recommend, update_embeddings, compute_embedding, append_blog_to_dataset
import numpy as np

# Initialize FastAPI app
app = FastAPI()

# Create the database tables
Base.metadata.create_all(bind=engine)

# Dependency to get the DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/recommendations/")
def get_recommendations(request: BlogRequest, db: Session = Depends(get_db)):
    recommendations = recommend(request.user_id, request.title, db)
    return {"recommended_blogs": recommendations}

@app.post("/upload_blog/")
def upload_blog(request: NewBlogRequest, db: Session = Depends(get_db)):
    global embeddings_matrix
    
    # Compute the embedding for the new blog
    new_embedding = compute_embedding(request.description)
    
    # Append the new blog to the dataset
    append_blog_to_dataset(request.title, request.description, request.description)
    
    # Update the embeddings matrix
    embeddings_matrix = np.vstack([embeddings_matrix, new_embedding])
    
    # Update the embeddings and similarity matrix
    update_embeddings()
    
    return {"message": "Blog uploaded and embeddings updated successfully."}