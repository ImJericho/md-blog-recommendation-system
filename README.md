# Blog Recommendation System

## Setup

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
Create a `.env` file with:
```
DATABASE_URL=your_database_url
```

4. Run the application:
```bash
uvicorn blog_recommender.main:app --reload
```

## API Endpoints

### Get Recommendations
- **GET** `/api/v1/recommendations/{user_id}/{blog_id}`
- Returns recommended blog IDs for a user based on a specific blog
- Optional `limit` parameter to specify number of recommendations (default: 10)

## Configuration

The recommendation weights can be adjusted in `profile.yaml`:
- `popularity`: Weight for popularity-based recommendations
- `recency`: Weight for recency-based recommendations
- `content_similarity`: Weight for content-based recommendations
- `user_similarity`: Weight for collaborative filtering

## Database Schema

### Users
- `user_id`: Primary key
- `name`: User's name
- `stream`: User's stream
- `class_name`: User's class

### Blogs
- `blog_id`: Primary key
- `title`: Blog title
- `content`: Blog content
- `tags`: JSON array of tags
- `exams`: JSON array of related exams
- `read_time`: Estimated read time
- `conclusion`: Blog conclusion
- `creation_date`: Creation timestamp

### Blog Metrics
- `blog_id`: Foreign key to Blogs
- `likes`: Number of likes
- `views`: Number of views

### Blog Similarities
- `blog_id_1`: First blog ID
- `blog_id_2`: Second blog ID
- `similarity_score`: Similarity score between blogs

### User History
- `user_id`: Foreign key to Users
- `blog_id`: Foreign key to Blogs
- `read_at`: Timestamp of when the blog was read 