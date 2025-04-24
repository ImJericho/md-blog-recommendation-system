from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.recommendation import router as recommendation_router
from .models.database import Base, engine

# Create database tables
# Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Blog Recommendation System",
    description="A hybrid recommendation system for blog posts",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendation_router, prefix="/api/v1", tags=["recommendations"])

@app.get("/")
async def root():
    return {"message": "Welcome to the Blog Recommendation System API"} 