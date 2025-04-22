import pandas as pd
import pickle
import numpy as np
# from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import UserActivity, User

# Load the dataset and embeddings
blogs_dataset = pd.read_csv("cleaned_blogs.csv")

# Load the embeddings matrix
with open('embeddings_matrix_mpnet.pkl', 'rb') as f:
    embeddings_matrix = pickle.load(f)

# Calculate cosine similarity between embeddings
similarity = cosine_similarity(embeddings_matrix)

# Load the paraphrase-mpnet-base-v2 model once
# model = SentenceTransformer('paraphrase-mpnet-base-v2')

def recommend(user_id: int, blog_title: str, db: Session):
   # Fetch the blog_id corresponding to the blog_title provided as an argument
   
    blog_row = blogs_dataset.loc[blogs_dataset['blog_title'] == blog_title]

    if blog_row.empty:
        raise HTTPException(status_code=404, detail="Blog title not found")

    blog_id = int(blog_row['blog_id'].values[0])
    
    # Record the user interaction with the given blog_title
    user_activity = UserActivity(user_id=user_id, blog_id=blog_id)
    db.add(user_activity)
    db.commit() 

    # Find the index of the given blog title
    index = blogs_dataset[blogs_dataset['blog_title'] == blog_title].index[0]
    
    # Calculate similarity scores
    distance = sorted(list(enumerate(similarity[index])), reverse=True, key=lambda vector: vector[1])
    
    # Get blogs the user has already interacted with
    seen_blog_ids = db.query(UserActivity.blog_id).filter(UserActivity.user_id == user_id).all()
    seen_blog_ids = {row[0] for row in seen_blog_ids}
    
    # Filter out already seen blogs
    recommended_blogs = []
    for i in distance[1:]:
        if blogs_dataset.iloc[i[0]]['blog_id'] not in seen_blog_ids:
            recommended_blogs.append(blogs_dataset.iloc[i[0]]['blog_title'])
        if len(recommended_blogs) >= 5:
            break

    return recommended_blogs

def update_embeddings():
    global embeddings_matrix, similarity

    # Recalculate the similarity matrix
    similarity = cosine_similarity(embeddings_matrix)
    
    # Save the updated dataset and embeddings matrix
    blogs_dataset.to_csv("cleaned_blogs.csv", index=False)
    with open('embeddings_matrix_mpnet.pkl', 'wb') as f:
        pickle.dump(embeddings_matrix, f)

def compute_embedding(description: str):
    return model.encode([description])[0]

def append_blog_to_dataset(title: str, description: str):
    new_data = {'blog_title': title, 'cleaned_description': description}
    blogs_dataset.loc[len(blogs_dataset)] = new_data

