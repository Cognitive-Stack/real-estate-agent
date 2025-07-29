#!/usr/bin/env python3
"""
MongoDB Connection and Setup Script
Run this after migration to set up MongoDB collections and indexes.
"""

import json
import os
from pathlib import Path
from urllib.parse import quote_plus
from pymongo import MongoClient, ASCENDING, DESCENDING
from pymongo.errors import ConnectionFailure, OperationFailure, ServerSelectionTimeoutError
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_mongodb_connection():
    """Test MongoDB connection with current environment variables."""
    try:
        # Build connection string
        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        host = os.getenv('MONGO_HOST', 'localhost')
        port = os.getenv('MONGO_PORT', '27017')
        db_name = os.getenv('MONGO_DB_NAME', 'real_estate_db')
        
        if username and password:
            # URL encode the username and password to handle special characters
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}"
            logger.info("Testing authenticated MongoDB connection...")
        else:
            connection_string = f"mongodb://{host}:{port}"
            logger.info("Testing non-authenticated MongoDB connection...")
        
        # Test connection
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,
            authSource='admin'
        )
        
        # Ping the database
        client.admin.command('ping')
        logger.info("✅ MongoDB connection successful!")
        
        # Test database access
        db = client[db_name]
        collections = db.list_collection_names()
        logger.info(f"✅ Database '{db_name}' access successful. Found {len(collections)} collections.")
        
        return True
        
    except OperationFailure as e:
        if "Authentication failed" in str(e) or "auth failed" in str(e).lower():
            logger.error("❌ Authentication failed. Please check your MongoDB username and password.")
        else:
            logger.error(f"❌ Database operation failed: {e}")
        return False
    except ConnectionFailure:
        logger.error("❌ Connection failed. Please check if MongoDB is running and connection details are correct.")
        return False
    except ServerSelectionTimeoutError:
        logger.error("❌ Connection timeout. MongoDB server might not be running or unreachable.")
        return False
    except Exception as e:
        logger.error(f"❌ Connection test failed: {e}")
        return False

def setup_mongodb_collections(connection_string=None, db_name=None):
    """Set up MongoDB collections with data and indexes."""
    
    # Use environment variables if parameters not provided
    if connection_string is None:
        # Build connection string with authentication if credentials are provided
        username = os.getenv('MONGO_USERNAME')
        password = os.getenv('MONGO_PASSWORD')
        host = os.getenv('MONGO_HOST', 'localhost')
        port = os.getenv('MONGO_PORT', '27017')
        
        if username and password:
            # URL encode the username and password to handle special characters
            encoded_username = quote_plus(username)
            encoded_password = quote_plus(password)
            connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}"
            logger.info("Using authenticated MongoDB connection")
        else:
            connection_string = os.getenv('MONGODB_URI', f'mongodb://{host}:{port}')
            logger.info("Using non-authenticated MongoDB connection")
    
    if db_name is None:
        db_name = os.getenv('MONGO_DB_NAME', 'real_estate_db')
    
    try:
        # Connect to MongoDB with authentication options
        client = MongoClient(
            connection_string,
            serverSelectionTimeoutMS=5000,  # 5 second timeout
            authSource='admin'  # Default auth database
        )
        db = client[db_name]
        
        # Test connection and authentication
        client.admin.command('ping')
        logger.info(f"Successfully connected to MongoDB: {db_name}")
        
        # Test database access
        collections = db.list_collection_names()
        logger.info(f"Database access confirmed. Existing collections: {len(collections)}")
        
        # Load migration data
        data_dir = Path("migrated_data")
        
        # Insert data into collections
        for json_file in data_dir.glob("*.json"):
            if json_file.name in ["indexes_schema.json", "migration_summary.json"]:
                continue
                
            collection_name = json_file.stem
            
            with open(json_file, 'r', encoding='utf-8') as f:
                documents = json.load(f)
            
            if documents:
                collection = db[collection_name]
                
                # Clear existing data
                collection.drop()
                
                # Insert new data
                result = collection.insert_many(documents)
                logger.info(f"Inserted {len(result.inserted_ids)} documents into {collection_name}")
        
        # Create indexes
        indexes_file = data_dir / "indexes_schema.json"
        if indexes_file.exists():
            with open(indexes_file, 'r', encoding='utf-8') as f:
                indexes_schema = json.load(f)
            
            for collection_name, indexes in indexes_schema.items():
                collection = db[collection_name]
                
                for index_def in indexes:
                    keys = index_def['keys']
                    options = {k: v for k, v in index_def.items() if k != 'keys'}
                    
                    # Convert string values to MongoDB constants
                    processed_keys = []
                    for field, direction in keys.items():
                        if direction == 1:
                            processed_keys.append((field, ASCENDING))
                        elif direction == -1:
                            processed_keys.append((field, DESCENDING))
                        elif direction == '2dsphere':
                            processed_keys.append((field, '2dsphere'))
                    
                    collection.create_index(processed_keys, **options)
                    logger.info(f"Created index on {collection_name}: {keys}")
        
        logger.info("MongoDB setup completed successfully")
        
    except OperationFailure as e:
        if "Authentication failed" in str(e) or "auth failed" in str(e).lower():
            logger.error("MongoDB authentication failed. Please check your username and password in the .env file.")
        else:
            logger.error(f"MongoDB operation failed: {e}")
    except ConnectionFailure:
        logger.error("Failed to connect to MongoDB. Please check if MongoDB is running and the connection details are correct.")
    except ServerSelectionTimeoutError:
        logger.error("Connection timeout. MongoDB server might not be running or unreachable.")
    except Exception as e:
        logger.error(f"Error setting up MongoDB: {e}")

if __name__ == "__main__":
    # First test the connection
    if test_mongodb_connection():
        # If connection is successful, proceed with setup
        setup_mongodb_collections()
    else:
        logger.error("MongoDB connection test failed. Please fix the connection issues before running setup.")
