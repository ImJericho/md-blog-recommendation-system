from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..models.database import get_db
from ..services.recommender import RecommenderService
from ..config.weights import RECOMMENDATION_COUNT

router = APIRouter()

@router.post("/new-blog/{blog_id}")
async def process_new_blog(blog_id: int, db: Session = Depends(get_db)):
    """
    Process a new blog post and update similarity scores.
    This endpoint should be called whenever a new blog is created.
    """
    try:
        recommender = RecommenderService(db)
        # Get all existing blogs
        existing_blogs = db.query(Blog).filter(Blog.blog_id != blog_id).all()
        
        # Calculate and store similarity scores with existing blogs
        for existing_blog in existing_blogs:
            recommender.calculate_content_similarity(blog_id, existing_blog.blog_id)
        
        return {"message": "Blog processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations/{user_id}/{blog_id}")
async def get_recommendations(
    user_id: int,
    blog_id: int,
    limit: int = RECOMMENDATION_COUNT,
    db: Session = Depends(get_db)
):
    """
    Get blog recommendations for a user based on a specific blog.
    """
    try:
        recommender = RecommenderService(db)
        recommendations = recommender.get_recommendations(user_id, blog_id)
        
        # Return top N recommendations
        return {
            "user_id": user_id,
            "blog_id": blog_id,
            "recommendations": recommendations[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 