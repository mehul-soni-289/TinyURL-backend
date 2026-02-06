"""
FastAPI Main Application
URL Shortener with Custom DSA Implementations
"""

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl, validator
import uvicorn
from typing import Optional
import re

# Import custom DSA modules
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dsa_modules.hash_map import HashMap
from dsa_modules.base62_codec import Base62Codec
from dsa_modules.lru_cache import LRUCache
from dsa_modules.trie import Trie
from dsa_modules.min_heap import TopKURLs
from dsa_modules.collision_detector import CollisionDetector
from config.database import db

# Configuration
API_BASE_URL = "https://tinyurl-backend-02o2.onrender.com"

# Initialize FastAPI app
app = FastAPI(
    title="TinyURL - Custom DSA Implementation",
    description="URL Shortener with custom Hash Map, LRU Cache, Trie, Min Heap, and Collision Detection",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize DSA structures
hash_map = HashMap(initial_capacity=1000)
lru_cache = LRUCache(capacity=100)
trie = Trie()
top_k_urls = TopKURLs(k=10)
collision_detector = CollisionDetector(hash_map)

# Request/Response Models
class ShortenRequest(BaseModel):
    url: str
    collision_strategy: Optional[str] = "linear"
    
    @validator('url')
    def validate_url(cls, v):
        # Basic URL validation
        url_pattern = re.compile(
            r'^https?://'  # http:// or https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
            r'localhost|'  # localhost...
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
            r'(?::\d+)?'  # optional port
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        
        if not url_pattern.match(v):
            raise ValueError('Invalid URL format')
        return v
    
    @validator('collision_strategy')
    def validate_strategy(cls, v):
        if v not in ['linear', 'regenerate', 'append']:
            raise ValueError('Invalid collision strategy. Must be: linear, regenerate, or append')
        return v


class ShortenResponse(BaseModel):
    success: bool
    original_url: str
    short_code: str
    short_url: str
    collision_detected: bool
    attempts: int
    strategy_used: Optional[str]
    cached: bool


@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "TinyURL - Custom DSA Implementation",
        "version": "1.0.0",
        "endpoints": {
            "shorten": "POST /api/shorten",
            "redirect": "GET /{short_code}",
            "stats": "GET /api/stats",
            "top_urls": "GET /api/top",
            "search": "GET /api/search?prefix={prefix}"
        }
    }


@app.post("/api/shorten", response_model=ShortenResponse)
async def shorten_url(request: ShortenRequest):
    """
    Shorten a URL using custom DSA implementations
    
    Process Flow:
    1. Validate URL
    2. Check LRU Cache for existing shortened URL
    3. Check database for existing URL
    4. Generate short code using Base62 encoding
    5. Detect and resolve collisions
    6. Store in all DSA structures
    7. Return shortened URL
    """
    original_url = request.url
    collision_strategy = request.collision_strategy
    
    # Step 1: Check LRU Cache
    cached_code = lru_cache.get(original_url)
    if cached_code:
        # URL already shortened and in cache
        return ShortenResponse(
            success=True,
            original_url=original_url,
            short_code=cached_code,
            short_url=f"{API_BASE_URL}/{cached_code}",
            collision_detected=False,
            attempts=1,
            strategy_used=None,
            cached=True
        )
    
    # Step 2: Check database for existing URL
    try:
        existing_url = await db.get_url_by_original(original_url)
        if existing_url and existing_url.get('short_code'):
            short_code = existing_url['short_code']
            
            # Add to cache and other structures
            lru_cache.put(original_url, short_code)
            hash_map.put(short_code, original_url)
            trie.insert(original_url)
            
            return ShortenResponse(
                success=True,
                original_url=original_url,
                short_code=short_code,
                short_url=f"{API_BASE_URL}/{short_code}",
                collision_detected=False,
                attempts=1,
                strategy_used=None,
                cached=False
            )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Step 3: Insert into database to get auto-increment ID
    try:
        url_id = await db.insert_url(original_url)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to insert URL: {str(e)}")
    
    # Step 4: Encode ID to Base62 short code
    short_code = Base62Codec.encode(url_id)
    
    # Step 5: Check for collision and resolve if needed
    collision_detected = False
    attempts = 1
    strategy_used = None
    
    if collision_detector.detect_collision(short_code):
        collision_detected = True
        try:
            short_code, attempts, strategy_used = collision_detector.resolve_collision(
                short_code, 
                strategy=collision_strategy,
                max_attempts=10
            )
        except ValueError as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    # Step 6: Update database with final short code
    try:
        await db.update_short_code(
            url_id, 
            short_code, 
            collision_resolved=collision_detected,
            resolution_strategy=strategy_used
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update short code: {str(e)}")
    
    # Step 7: Store in all DSA structures
    hash_map.put(short_code, original_url)
    lru_cache.put(original_url, short_code)
    trie.insert(original_url)
    
    # Step 8: Return response
    return ShortenResponse(
        success=True,
        original_url=original_url,
        short_code=short_code,
        short_url=f"{API_BASE_URL}/{short_code}",
        collision_detected=collision_detected,
        attempts=attempts,
        strategy_used=strategy_used,
        cached=False
    )


@app.get("/{short_code}")
async def redirect_url(short_code: str):
    """
    Redirect to original URL
    
    Process:
    1. Check LRU Cache
    2. Check HashMap
    3. Query database
    4. Increment click count
    5. Update analytics
    6. Redirect
    """
    # Step 1: Check LRU Cache (by short_code as key for reverse lookup)
    # Note: We need to modify our approach - cache stores original_url -> short_code
    # For redirect, we need short_code -> original_url
    
    original_url = None
    
    # Step 2: Check HashMap first (fastest)
    original_url = hash_map.get(short_code)
    
    # Step 3: If not in HashMap, query database
    if not original_url:
        try:
            url_data = await db.get_url_by_short_code(short_code)
            if not url_data:
                raise HTTPException(status_code=404, detail="Short URL not found")
            
            original_url = url_data['original_url']
            
            # Add to HashMap for future lookups
            hash_map.put(short_code, original_url)
            lru_cache.put(original_url, short_code)
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    
    # Step 4: Increment click count
    try:
        new_clicks = await db.increment_clicks(short_code)
        
        # Step 5: Update Trie frequency
        trie.update_frequency(original_url)
        
        # Step 6: Update Top K URLs
        url_data = await db.get_url_by_short_code(short_code)
        if url_data:
            top_k_urls.add_or_update(short_code, new_clicks, url_data)
        
    except Exception as e:
        # Don't fail redirect if analytics update fails
        print(f"Analytics update error: {str(e)}")
    
    # Step 7: Redirect to original URL
    return RedirectResponse(url=original_url, status_code=301)


@app.get("/api/stats")
async def get_stats():
    """
    Get comprehensive statistics about all DSA structures
    """
    return {
        "hash_map": hash_map.get_stats(),
        "lru_cache": lru_cache.get_stats(),
        "trie": trie.get_stats(),
        "collision_detector": collision_detector.get_collision_stats()
    }


@app.get("/api/top")
async def get_top_urls():
    """
    Get top K URLs by click count
    Uses Min Heap for efficient tracking
    """
    try:
        # Get from database for accurate data
        top_urls = await db.get_top_urls(limit=10)
        return {
            "success": True,
            "top_urls": top_urls
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@app.get("/api/search")
async def search_urls(prefix: str, max_results: int = 5):
    """
    Search URLs by prefix using Trie
    Provides autocomplete functionality
    """
    if not prefix:
        raise HTTPException(status_code=400, detail="Prefix parameter is required")
    
    results = trie.search_prefix(prefix, max_results=max_results)
    
    return {
        "success": True,
        "prefix": prefix,
        "results": [
            {
                "url": url,
                "frequency": freq
            }
            for url, freq in results
        ]
    }


@app.on_event("startup")
async def startup_event():
    """
    Initialize application on startup
    Load existing URLs from database into DSA structures
    """
    print("🚀 Starting TinyURL application...")
    print("📊 Loading existing URLs from database...")
    
    try:
        # Load all URLs from database
        all_urls = await db.get_all_urls()
        
        for url_data in all_urls:
            short_code = url_data.get('short_code')
            original_url = url_data.get('original_url')
            clicks = url_data.get('clicks', 0)
            
            if short_code and original_url:
                # Populate HashMap
                hash_map.put(short_code, original_url)
                
                # Populate Trie
                trie.insert(original_url, frequency=clicks)
                
                # Populate Top K URLs
                top_k_urls.add_or_update(short_code, clicks, url_data)
        
        print(f"✅ Loaded {len(all_urls)} URLs into memory")
        print(f"📈 HashMap size: {hash_map.size}")
        print(f"🌳 Trie URLs: {trie.total_urls}")
        print(f"🔥 Top URLs tracked: {top_k_urls.heap.size}")
        
    except Exception as e:
        print(f"⚠️  Warning: Could not load URLs from database: {str(e)}")
        print("   Application will continue with empty data structures")


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
