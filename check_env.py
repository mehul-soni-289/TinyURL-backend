"""
Environment Variables Checker
Run this script to verify your .env file is set up correctly
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def check_env():
    """Check if environment variables are properly configured"""
    
    print("=" * 60)
    print("🔍 TinyURL Environment Variables Checker")
    print("=" * 60)
    print()
    
    # Get the backend directory
    backend_dir = Path(__file__).resolve().parent
    env_path = backend_dir / '.env'
    
    # Check if .env file exists
    print(f"📁 Checking for .env file at: {env_path}")
    if env_path.exists():
        print("✅ .env file found!")
    else:
        print("❌ .env file NOT found!")
        print()
        print("📝 To create .env file:")
        print(f"   1. Copy .env.example to .env")
        print(f"   2. Edit .env and add your Supabase credentials")
        print()
        return False
    
    print()
    
    # Load environment variables
    print("📥 Loading environment variables...")
    load_dotenv(dotenv_path=env_path)
    print()
    
    # Check SUPABASE_URL
    print("🔑 Checking SUPABASE_URL...")
    supabase_url = os.getenv("SUPABASE_URL")
    if supabase_url:
        if supabase_url == "your_supabase_project_url_here":
            print("⚠️  SUPABASE_URL is still the placeholder value!")
            print("   Please update it with your actual Supabase project URL")
        elif supabase_url.startswith("https://") and "supabase.co" in supabase_url:
            print(f"✅ SUPABASE_URL is set: {supabase_url[:30]}...")
        else:
            print(f"⚠️  SUPABASE_URL format looks incorrect: {supabase_url[:30]}...")
            print("   Expected format: https://xxxxx.supabase.co")
    else:
        print("❌ SUPABASE_URL is not set!")
    
    print()
    
    # Check SUPABASE_KEY
    print("🔑 Checking SUPABASE_KEY...")
    supabase_key = os.getenv("SUPABASE_KEY")
    if supabase_key:
        if supabase_key == "your_supabase_anon_public_key_here":
            print("⚠️  SUPABASE_KEY is still the placeholder value!")
            print("   Please update it with your actual Supabase anon/public key")
        elif supabase_key.startswith("eyJ"):
            print(f"✅ SUPABASE_KEY is set: {supabase_key[:20]}...")
        else:
            print(f"⚠️  SUPABASE_KEY format looks incorrect")
            print("   Expected format: eyJhbGc... (JWT token)")
    else:
        print("❌ SUPABASE_KEY is not set!")
    
    print()
    print("=" * 60)
    
    # Final verdict
    if (supabase_url and supabase_key and 
        supabase_url != "your_supabase_project_url_here" and
        supabase_key != "your_supabase_anon_public_key_here" and
        supabase_url.startswith("https://") and
        supabase_key.startswith("eyJ")):
        print("✅ Environment variables are properly configured!")
        print("✅ You can now start the backend server")
        print()
        print("Run: cd api && python main.py")
        return True
    else:
        print("❌ Environment variables need to be configured")
        print()
        print("📝 Steps to fix:")
        print("1. Open backend/.env in your text editor")
        print("2. Replace placeholder values with your Supabase credentials")
        print("3. Get credentials from: https://supabase.com → Settings → API")
        print("4. Save the file and run this script again")
        return False
    
    print("=" * 60)

if __name__ == "__main__":
    check_env()
