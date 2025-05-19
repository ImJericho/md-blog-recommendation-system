# Blog Recommendation System

## Setup

1. Make sure you have Poetry installed:
```bash
pip install poetry
```

2. Install the dependencies:
```bash
poetry install
```

2. Create a virtual environment:
```bash
poetry shell
```

3. Run the application:
```bash
poetry run uvicorn main:app --reload 
```

## API Endpoints

### Post Recommendations
- **POST** `/api/v1/recommendations`
- Arguments are "blog_id":INT, and "limit":INT 
- Returns recommended blog IDs for a user based on a specific blog
- Optional `limit` parameter to specify number of recommendations (default: 10)

## Configuration

The recommendation weights can be adjusted in `profile.yaml`:
- `popularity`: Weight for popularity-based recommendations
- `recency`: Weight for recency-based recommendations
- `content_similarity`: Weight for content-based recommendations

## Database Schema

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