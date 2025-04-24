"""
Configuration file for recommendation weights.
These weights determine the importance of each recommendation factor.
"""

RECOMMENDATION_WEIGHTS = {
    'popularity': 0.3,      # Based on likes and views
    'recency': 0.2,         # Based on creation date
    'content_similarity': 0.3,  # Based on content similarity
    'user_similarity': 0.2  # Based on similar users' preferences
}

# Minimum threshold for similarity scores
SIMILARITY_THRESHOLD = 0.5

# Number of similar users to consider for collaborative filtering
SIMILAR_USERS_COUNT = 5

# Number of recommendations to return
RECOMMENDATION_COUNT = 10 