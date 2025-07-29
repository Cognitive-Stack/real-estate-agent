"""
Base class for real estate data tools.

This module provides the base MongoDB connection functionality
for all real estate data query tools.
"""

import os
from typing import Dict
from urllib.parse import quote_plus
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, OperationFailure
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class BaseRealEstateTools:
    """Base class for real estate data tools with MongoDB connection."""
    
    def __init__(self, connection_string=None, db_name=None):
        """
        Initialize the data tools with MongoDB connection.
        
        Args:
            connection_string: MongoDB connection string. If None, uses environment variables.
            db_name: Database name. If None, uses environment variable.
        """
        # Build connection string from environment variables if not provided
        if connection_string is None:
            username = os.getenv('MONGO_USERNAME')
            password = os.getenv('MONGO_PASSWORD')
            host = os.getenv('MONGO_HOST', 'localhost')
            port = os.getenv('MONGO_PORT', '27017')
            
            if username and password:
                encoded_username = quote_plus(username)
                encoded_password = quote_plus(password)
                connection_string = f"mongodb://{encoded_username}:{encoded_password}@{host}:{port}"
            else:
                connection_string = os.getenv('MONGODB_URI', f'mongodb://{host}:{port}')
        
        if db_name is None:
            db_name = os.getenv('MONGO_DB_NAME', 'real_estate_db')
        
        self.connection_string = connection_string
        self.db_name = db_name
        self.client = None
        self.db = None
        
        # Collection names mapping
        self.collections = {
            'properties': 'properties',
            'property_groups': 'property_groups',
            'locations': 'locations',
            'developers': 'developers',
            'project_overview': 'project_overview',
            'physical_features': 'physical_features',
            'investment_info': 'investment_info',
            'legal_info': 'legal_info',
            'sales_policy': 'sales_policy',
            'transportation': 'transportation',
            'residential_environment': 'residential_environment',
            'living_experience': 'living_experience',
            'design_layout': 'design_layout',
            'equipment_materials': 'equipment_materials',
            'contractors': 'contractors',
            'legal_status': 'legal_status'
        }
        
        # Initialize connection
        self._connect()
    
    def _connect(self):
        """Establish connection to MongoDB."""
        try:
            self.client = MongoClient(
                self.connection_string,
                serverSelectionTimeoutMS=5000,
                authSource='admin'
            )
            self.db = self.client[self.db_name]
            # Test connection
            self.client.admin.command('ping')
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            self.client = None
            self.db = None
    
    def _ensure_connection(self):
        """Ensure MongoDB connection is active."""
        if self.client is None or self.db is None:
            self._connect()
        if self.client is None or self.db is None:
            raise ConnectionError("Could not establish MongoDB connection")
