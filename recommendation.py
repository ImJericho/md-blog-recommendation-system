import pandas as pd
import pickle
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import UserActivity, User
from sentence_transformers import SentenceTransformer

# Load model once globally
model = SentenceTransformer('paraphrase-mpnet-base-v2')

# Load dataset
blogs_dataset = pd.read_csv("cleaned_blogs.csv")

# Recompute enhanced descriptions for embedding (title + tags + desc)
def combine_text(row):
    return f"{row['blog_title']} {row['tags']} {row['description']}"

blogs_dataset["full_text"] = blogs_dataset.apply(combine_text, axis=1)

# Load or compute embeddings
with open('embeddings_matrix_mpnet.pkl', 'rb') as f:
    embeddings_matrix = pickle.load(f)

# Precompute cosine similarity
similarity = cosine_similarity(embeddings_matrix)

def recommend(user_id: int, blog_title: str, db: Session):
    # Step 1: Validate blog title
    blog_row = blogs_dataset[blogs_dataset['blog_title'] == blog_title]
    if blog_row.empty:
        raise HTTPException(status_code=404, detail="Blog title not found")

    blog_id = int(blog_row['blog_id'].values[0])
    index = blog_row.index[0]

    # Step 2: Log user activity
    user_activity = UserActivity(user_id=user_id, blog_id=blog_id)
    db.add(user_activity)
    db.commit()

    # Step 3: Get user's exam interest
    user_exam = db.query(User).filter(User.id == user_id).first()
    if not user_exam:
        raise HTTPException(status_code=404, detail="User not found")
    user_exam_interest = user_exam.stream  # You can also add a specific 'exam_interest' field in your model

    # Step 4: Calculate similarity scores for the blog
    distances = list(enumerate(similarity[index]))

    # Step 5: Filter by exam interest
    exam_filtered_indices = blogs_dataset[
        blogs_dataset['exam'] == user_exam_interest
    ].index
    filtered_distances = [(i, score) for i, score in distances if i in exam_filtered_indices]

    # Step 6: Exclude already seen blogs
    seen_ids = {
        row[0] for row in db.query(UserActivity.blog_id).filter(UserActivity.user_id == user_id).all()
    }

    # Step 7: Prepare response
    recommended = []
    for i, score in sorted(filtered_distances, key=lambda x: x[1], reverse=True):
        blog = blogs_dataset.iloc[i]
        if blog['blog_id'] not in seen_ids:
            recommended.append({
                "blog_id": blog["blog_id"],
                "title": blog["blog_title"],
                "tags": blog["tags"],
                "exam": blog["exam"],
                "read_time": blog.get("read_time", 3),
                "score": round(float(score), 3)
            })
        if len(recommended) >= 5:
            break

    return recommended

# Add a new blog and regenerate embeddings
def add_new_blog(title: str, description: str, tags: str, exam: str):
    global embeddings_matrix, similarity

    new_id = blogs_dataset['blog_id'].max() + 1
    full_text = f"{title} {tags} {description}"
    new_vector = model.encode([full_text])[0]

    # Add to dataframe
    new_row = {
        "blog_id": new_id,
        "blog_title": title,
        "tags": tags,
        "exam": exam,
        "cleaned_description": description,
        "full_text": full_text
    }
    blogs_dataset.loc[len(blogs_dataset)] = new_row

    # Update embeddings
    embeddings_matrix = np.vstack([embeddings_matrix, new_vector])
    similarity = cosine_similarity(embeddings_matrix)

    # Save both
    blogs_dataset.to_csv("cleaned_blogs.csv", index=False)
    with open('embeddings_matrix_mpnet.pkl', 'wb') as f:
        pickle.dump(embeddings_matrix, f)

    return f"✅ Blog '{title}' added with ID {new_id}."

