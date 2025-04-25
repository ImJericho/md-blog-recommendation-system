from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import yaml
from models.database import get_db
from services.recommender import RecommenderService


# Load configuration from YAML file
with open("profile.yaml", "r") as file:
    config = yaml.safe_load(file)
RECOMMENDATION_COUNT = config.get("recommendation_count")

router = APIRouter()

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
    print("Starting recommendation process...")
    try:
        recommender = RecommenderService(db)
        recommendations = recommender.get_recommendations(user_id, blog_id)
        
        return {
            "user_id": user_id,
            "blog_id": blog_id,
            "recommendations": recommendations[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 