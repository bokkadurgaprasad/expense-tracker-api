"""
MongoDB connection management using PyMongo driver
"""
from pymongo import MongoClient
from typing import Optional
from app.config import settings

# Global database client and database instances
mongo_client: Optional[MongoClient] = None
database = None


def connect_to_mongo():
    """Establish connection to MongoDB using PyMongo driver"""
    global mongo_client, database
    
    try:
        mongo_client = MongoClient(settings.mongodb_uri)
        database = mongo_client[settings.database_name]
        
        # Test the connection
        mongo_client.admin.command('ping')
        print(f"Connected to MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise


def close_mongo_connection():
    """Close MongoDB connection"""
    global mongo_client
    
    if mongo_client:
        mongo_client.close()
        print("MongoDB connection closed")


def get_database():
    """Get database instance for dependency injection"""
    if database is None:
        raise RuntimeError("Database not initialized. Call connect_to_mongo() first.")
    return database
