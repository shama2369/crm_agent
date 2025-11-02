#!/usr/bin/env python3
"""
Setup script for CRM Agent
This script helps you configure the required environment variables.
"""

import os

def create_env_file():
    """Create a .env file with the required configuration"""
    env_content = """# OpenAI API Configuration
# Get your API key from: https://platform.openai.com/api-keys
OPENAI_API_KEY=your_openai_api_key_here

# MongoDB Configuration (optional - will fallback to local JSON files if not set)
# MONGO_URI=mongodb://localhost:27017/crm
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write(env_content)
        print("SUCCESS: Created .env file")
        print("INFO: Please edit .env file and add your OpenAI API key")
    else:
        print("WARNING: .env file already exists")

def check_environment():
    """Check if environment variables are properly set"""
    from dotenv import load_dotenv
    load_dotenv()
    
    openai_key = os.getenv("OPENAI_API_KEY")
    mongo_uri = os.getenv("MONGO_URI")
    
    print("\nEnvironment Check:")
    print(f"OPENAI_API_KEY: {'SET' if openai_key and openai_key != 'your_openai_api_key_here' else 'NOT SET'}")
    print(f"MONGO_URI: {'SET' if mongo_uri else 'NOT SET (will use local JSON files)'}")
    
    if not openai_key or openai_key == 'your_openai_api_key_here':
        print("\nERROR: OPENAI_API_KEY is required!")
        print("Please edit .env file and add your OpenAI API key")
        return False
    
    return True

def main():
    print("CRM Agent Setup")
    print("=" * 50)
    
    create_env_file()
    
    try:
        if check_environment():
            print("\nSUCCESS: Setup complete! You can now run the application.")
            print("Run: uvicorn app:app --reload")
        else:
            print("\nERROR: Setup incomplete. Please configure your OpenAI API key.")
    except ImportError:
        print("\nWARNING: python-dotenv not installed. Run: pip install python-dotenv")

if __name__ == "__main__":
    main()
