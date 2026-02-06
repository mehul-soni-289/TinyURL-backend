"""
Supabase Database Configuration
Handles connection and operations with PostgreSQL database
"""

import os
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env file
# Get the directory where this file is located
current_dir = Path(__file__).resolve().parent
# Go up one level to backend directory where .env should be
env_path = current_dir.parent / '.env'

# Load the .env file
load_dotenv(dotenv_path=env_path)

# Print confirmation (for debugging)
if os.getenv("SUPABASE_URL"):
    print(f"✅ Environment variables loaded from: {env_path}")
else:
    print(f"⚠️  Warning: .env file not found at {env_path}")


class Database:
    """
    Database connection and operations handler
    """
    
    def __init__(self):
        """Initialize Supabase client"""
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")
        
        if not supabase_url or not supabase_key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY must be set in environment variables"
            )
        
        self.client: Client = create_client(supabase_url, supabase_key)
    
    async def insert_url(self, original_url):
        """
        Insert a new URL and get auto-generated ID
        
        Args:
            original_url (str): Original URL to shorten
            
        Returns:
            int: Auto-generated ID from database
        """
        try:
            result = self.client.table("urls").insert({
                "original_url": original_url,
                "clicks": 0
            }).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]["id"]
            else:
                raise Exception("Failed to insert URL into database")
        except Exception as e:
            raise Exception(f"Database insert error: {str(e)}")
    
    async def update_short_code(self, url_id, short_code, collision_resolved=False, resolution_strategy=None):
        """
        Update the short code for a URL
        
        Args:
            url_id (int): Database ID of the URL
            short_code (str): Generated short code
            collision_resolved (bool): Whether collision was resolved
            resolution_strategy (str): Strategy used for collision resolution
        """
        try:
            update_data = {
                "short_code": short_code,
                "collision_resolved": collision_resolved
            }
            
            if resolution_strategy:
                update_data["resolution_strategy"] = resolution_strategy
            
            self.client.table("urls").update(update_data).eq("id", url_id).execute()
        except Exception as e:
            raise Exception(f"Database update error: {str(e)}")
    
    async def get_url_by_short_code(self, short_code):
        """
        Get URL data by short code
        
        Args:
            short_code (str): Short code to lookup
            
        Returns:
            dict: URL data or None if not found
        """
        try:
            result = self.client.table("urls").select("*").eq("short_code", short_code).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            raise Exception(f"Database query error: {str(e)}")
    
    async def get_url_by_original(self, original_url):
        """
        Check if original URL already exists
        
        Args:
            original_url (str): Original URL to check
            
        Returns:
            dict: URL data or None if not found
        """
        try:
            result = self.client.table("urls").select("*").eq("original_url", original_url).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0]
            return None
        except Exception as e:
            raise Exception(f"Database query error: {str(e)}")
    
    async def increment_clicks(self, short_code):
        """
        Increment click count for a URL
        
        Args:
            short_code (str): Short code of URL
            
        Returns:
            int: New click count
        """
        try:
            # Get current clicks
            result = self.client.table("urls").select("clicks").eq("short_code", short_code).execute()
            
            if result.data and len(result.data) > 0:
                current_clicks = result.data[0]["clicks"]
                new_clicks = current_clicks + 1
                
                # Update clicks
                self.client.table("urls").update({"clicks": new_clicks}).eq("short_code", short_code).execute()
                
                return new_clicks
            return 0
        except Exception as e:
            raise Exception(f"Database update error: {str(e)}")
    
    async def get_top_urls(self, limit=10):
        """
        Get top URLs by click count
        
        Args:
            limit (int): Number of top URLs to retrieve
            
        Returns:
            list: List of URL data sorted by clicks
        """
        try:
            result = self.client.table("urls").select("*").order("clicks", desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Database query error: {str(e)}")
    
    async def get_all_urls(self):
        """
        Get all URLs from database
        
        Returns:
            list: List of all URL data
        """
        try:
            result = self.client.table("urls").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            raise Exception(f"Database query error: {str(e)}")
    
    async def delete_url(self, short_code):
        """
        Delete a URL by short code
        
        Args:
            short_code (str): Short code to delete
            
        Returns:
            bool: True if deleted, False otherwise
        """
        try:
            self.client.table("urls").delete().eq("short_code", short_code).execute()
            return True
        except Exception as e:
            raise Exception(f"Database delete error: {str(e)}")


# Global database instance
db = Database()
