from typing import List, Dict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
import numpy as np
import yaml
from models.database import Blog, BlogMetrics, BlogSimilarity, User
from sentence_transformers import SentenceTransformer
from torch.nn import functional as F

class RecommenderService:
    def __init__(self, db: Session):
        self.db = db
        # Load configuration from YAML file
        with open("profile.yaml", "r") as file:
            self.config = yaml.safe_load(file)
        
        # Store configuration values as instance variables
        self.recommendation_weights = self.config["recommendation_weights"]
        self.similarity_threshold = self.config["similarity_threshold"]
        self.similar_users_count = self.config["similar_users_count"]

    def calculate_popularity_score(self, blog: Blog) -> float:
        """Calculate popularity score based on likes and views"""
        metrics = blog.metrics
        if not metrics:
            return 0.0
        
        if metrics.likes is None or metrics.views is None:
            return 0.0
        
        # Normalize likes and views
        max_likes = self.db.query(BlogMetrics.likes).order_by(BlogMetrics.likes.desc()).first()[0] or 1
        max_views = self.db.query(BlogMetrics.views).order_by(BlogMetrics.views.desc()).first()[0] or 1
        
        likes_score = metrics.likes / max_likes
        views_score = metrics.views / max_views
        
        return (likes_score + views_score) / 2

    def calculate_recency_score(self, blog: Blog) -> float:
        """Calculate recency score based on creation date"""
        now = datetime.utcnow()
        # Check if creation_date exists
        if not blog.creation_date:
            return 0.0
        
        days_old = (now - blog.creation_date).days
        
        # Score decreases exponentially with age
        return np.exp(-days_old / 30)  # 30 days half-life

    def calculate_content_similarity(self, blog_id: int, other_blog_id: int) -> float:
        """Calculate content similarity between two blogs using sentence embeddings"""
        # Check if similarity is already cached in database
        similarity = self.db.query(BlogSimilarity).filter(
            ((BlogSimilarity.blog_id_1 == blog_id) & (BlogSimilarity.blog_id_2 == other_blog_id)) |
            ((BlogSimilarity.blog_id_1 == other_blog_id) & (BlogSimilarity.blog_id_2 == blog_id))
        ).first()
        
        if similarity:
            return similarity.similarity_score
        
        # If not found in cache, calculate and store
        blog1 = self.db.query(Blog).filter(Blog.blog_id == blog_id).first()
        blog2 = self.db.query(Blog).filter(Blog.blog_id == other_blog_id).first()
        
        if not blog1 or not blog2:
            return 0.0
        
        # Load pre-trained sentence transformer model (only loads once)
        if not hasattr(self, 'sentence_model'):
            self.sentence_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
        
        # Prepare text with weighted components
        title1 = blog1.title
        title2 = blog2.title
        content1 = blog1.content
        content2 = blog2.content
        content1_lines = content1.split('.')
        content2_lines = content2.split('.')
        intro1 = '.'.join(content1_lines[:3]) if len(content1_lines) >= 3 else content1
        intro2 = '.'.join(content2_lines[:3]) if len(content2_lines) >= 3 else content2
        conclusion1 = '.'.join(content1_lines[-4:]) if len(content1_lines) >= 4 else content1
        conclusion2 = '.'.join(content2_lines[-4:]) if len(content2_lines) >= 4 else content2

        # Combine text with weights
        text1 = f"{title1}. {intro1}. {content1} {conclusion1}"
        text2 = f"{title2}. {intro2}. {content2} {conclusion2}"

        # Generate embeddings
        embeddings1 = self.sentence_model.encode(text1, convert_to_tensor=True)
        embeddings2 = self.sentence_model.encode(text2, convert_to_tensor=True)
        
        # Calculate similarity using dot product with L2 normalization (angular similarity)
        similarity_score = float(F.cosine_similarity(embeddings1.unsqueeze(0), embeddings2.unsqueeze(0))[0])
        
        # Store the similarity score
        new_similarity = BlogSimilarity(
            blog_id_1=blog_id,
            blog_id_2=other_blog_id,
            similarity_score=similarity_score
        )
        self.db.add(new_similarity)
        self.db.commit()
        
        return similarity_score

    # def find_similar_users(self, user_id: int) -> List[int]:
    #     """Find users with similar reading patterns"""
    #     current_user = self.db.query(User).filter(User.user_id == user_id).first()
    #     if not current_user:
    #         return []
        
    #     # Get all users and their read blogs
    #     all_users = self.db.query(User).all()
    #     user_similarities = []
        
    #     for user in all_users:
    #         if user.user_id == user_id:
    #             continue
                
    #         # Calculate Jaccard similarity between read blogs
    #         current_blogs = set(b.blog_id for b in current_user.read_history)
    #         other_blogs = set(b.blog_id for b in user.read_history)
            
    #         if not current_blogs or not other_blogs:
    #             continue
                
    #         intersection = len(current_blogs & other_blogs)
    #         union = len(current_blogs | other_blogs)
    #         similarity = intersection / union if union > 0 else 0
            
    #         user_similarities.append((user.user_id, similarity))
        
    #     # Sort by similarity and return top N users
    #     user_similarities.sort(key=lambda x: x[1], reverse=True)
    #     return [user_id for user_id, _ in user_similarities[:self.similar_users_count]]

    # def calculate_user_similarity(self, user_id: int, other_user_id: int) -> float:
    #     # Find similar users and their preferences
    #     similar_users = self.find_similar_users(user_id)
    #     user_similarity_score = 0.0
    #     if similar_users:
    #         # Calculate average preference of similar users
    #         similar_user_preferences = []
    #         for similar_user_id in similar_users:
    #             similar_user = self.db.query(User).filter(User.user_id == similar_user_id).first()
    #             if similar_user and blog in similar_user.read_history:
    #                 similar_user_preferences.append(1.0)
    #             else:
    #                 similar_user_preferences.append(0.0)
    #         user_similarity_score = sum(similar_user_preferences) / len(similar_user_preferences)

    #     return user_similarity_score

    def get_recommendations(self, user_id: int, blog_id: int) -> List[int]:
        """Get recommendations for a user based on a specific blog"""
        # Get all blogs except the current one
        all_blogs = self.db.query(Blog).filter(Blog.blog_id != blog_id).all()
        print(self.db.query(Blog))
        # Calculate scores for each blog
        blog_scores = []
        for blog in all_blogs:
            popularity_score = self.calculate_popularity_score(blog) 
            recency_score = self.calculate_recency_score(blog)
            content_similarity_score = self.calculate_content_similarity(blog_id, blog.blog_id)
            # user_similarity_score = self.calculate_user_similarity(user_id, blog.blog_id)
    
            final_score = (
                self.recommendation_weights['popularity'] * popularity_score +
                self.recommendation_weights['recency'] * recency_score +
                self.recommendation_weights['content_similarity'] * content_similarity_score
                # self.recommendation_weights['user_similarity'] * user_similarity_score
            )
            
            blog_scores.append((blog.blog_id, final_score))
        
        blog_scores.sort(key=lambda x: x[1], reverse=True)
        return [blog_id for blog_id, _ in blog_scores]
        