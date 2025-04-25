import csv
from datetime import datetime
import json
from sqlalchemy.orm import Session
from ..models.database import Blog, BlogMetrics, SessionLocal, engine

def import_cleaned_blogs(cleaned_blogs_file: str):
    """Import cleaned blogs data into the database from a CSV file"""
    try:
        # Read the cleaned blogs CSV file
        blogs_data = []
        with open(cleaned_blogs_file, 'r', encoding='utf-8') as f:
            csv_reader = csv.DictReader(f)
            for row in csv_reader:
                blogs_data.append(row)
        
        # Create a new session
        db = SessionLocal()
        
        try:
            # Import each blog
            i = 0
            for blog_data in blogs_data:
                # Handle lists stored as strings
                print(f"Processing blog_entry {blog_data.get('blog_id', 'unknown')} for {i}")
                i += 1
                
                # Set default values for missing fields
                blog_id = blog_data.get('blog_id')
                if not blog_id:
                    print("Skipping entry with no blog_id")
                    continue
                    
                # Convert tags and exams from string to list with defaults
                # tags = json.loads(blog_data.get('tags', '[]')) if blog_data.get('tags') else []
                # exams = json.loads(blog_data.get('exams', '[]')) if blog_data.get('exams') else []
                tags = blog_data.get('tags', '')
                exams = blog_data.get('exams', '')
                
                # Create blog entry with defaults for missing fields
                blog = Blog(
                    blog_id=blog_id,
                    title=blog_data.get('title', 'Untitled Blog'),
                    content=blog_data.get('description', ''),
                    tags=json.dumps(tags),
                    exams=json.dumps(exams),
                    read_time=int(blog_data.get('read_time', 5)) if blog_data.get('read_time') else 5,
                    conclusion=blog_data.get('conclusion', 'No conclusion provided.'),
                    creation_date=datetime.strptime(blog_data.get('creation_date', '2023-01-01'), '%Y-%m-%d')
                )
                db.add(blog)

                print(blog)
                
                # Create corresponding metrics with defaults
                # metrics = BlogMetrics(
                #     blog_id=blog_id,
                #     likes=int(blog_data.get('likes', 0)) if blog_data.get('likes') else 0,
                #     views=int(blog_data.get('views', 0)) if blog_data.get('views') else 0
                # )
                # db.add(metrics)
            
            db.commit()
            print(f"Successfully imported {len(blogs_data)} blogs")
            
        except Exception as e:
            print(f"Error importing blogs: {e}")
            db.rollback()
        finally:
            db.close()
            
    except FileNotFoundError:
        print(f"Error: File {cleaned_blogs_file} not found")
    except csv.Error:
        print(f"Error: Invalid CSV format in {cleaned_blogs_file}")

if __name__ == "__main__":
    # Assuming the cleaned blogs file is in the data directory
    cleaned_blogs_file = "data/cleaned_blogs.csv"
    import_cleaned_blogs(cleaned_blogs_file)