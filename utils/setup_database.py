from .populate_db import populate_database
from .import_cleaned_blogs import import_cleaned_blogs
import os

def setup_database():
    """Set up and populate the database with sample data and cleaned blogs"""
    # Create data directory if it doesn't exist
    os.makedirs("data", exist_ok=True)
    
    # First, populate with sample data
    print("Populating database with sample data...")
    populate_database()
    
    # Then, try to import cleaned blogs if the file exists
    cleaned_blogs_file = "data/cleaned_blogs.csv"
    if os.path.exists(cleaned_blogs_file):
        print("\nImporting cleaned blogs...")
        import_cleaned_blogs(cleaned_blogs_file)
    else:
        print("\nNo cleaned_blogs.json file found. Skipping import.")

if __name__ == "__main__":
    setup_database() 