from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from models.database import get_db
from services.recommender import RecommenderService
from pydantic import BaseModel
import traceback

# Create a request model
class RecommendationRequest(BaseModel):
    blog_id: int
    limit: int

router = APIRouter()

@router.post("/recommendations")
async def get_recommendations(
    request: RecommendationRequest,
    db: Session = Depends(get_db)
):
    if request.blog_id == None or request.limit == None:
        return HTTPException(status_code=400, detail="Blog ID and limit must be provided")
    try:
        print("Initializing RecommenderService...")
        print(f"DB session type: {type(db)}")
        print(f"DB session is None: {db is None}")
        recommender = RecommenderService(db)
        print("RecommenderService initialized")
        recommendations = recommender.get_recommendations(request.blog_id)
        
        return {
            "blog_id": request.blog_id,
            "recommendations": recommendations[:request.limit]
        }
    except Exception as e:
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e)) 