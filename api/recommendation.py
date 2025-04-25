from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import yaml
from ..models.database import get_db
from ..services.recommender import RecommenderService


# Load configuration from YAML file
config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "weights.yaml")
with open(config_path, "r") as file:
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
        
        # Return top N recommendations
        return {
            "user_id": user_id,
            "blog_id": blog_id,
            "recommendations": recommendations[:limit]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 