import requests
import uuid
from quaries_user import insert_api_key, delete_api_key

# Base URL of the API
BASE_URL = "http://localhost:8087"

def create_session(api_key: str):
    """Create a session using an API key"""
    headers = {"api-key": api_key}
    response = requests.post(
        f"{BASE_URL}/api-keys/session",
        headers=headers
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to create session: {response.text}")
    
    # Return the session cookie
    return response.cookies.get("session_token")

def get_logs(session_token: str):
    """Get logs using a session token"""
    cookies = {"session_token": session_token}
    response = requests.get(
        f"{BASE_URL}/get-logs",
        cookies=cookies
    )
    
    if response.status_code != 200:
        raise Exception(f"Failed to get logs: {response.text}")
    
    return response.json()

def example_usage(api_key: str):
    try:
        # Step 1: Create a session
        session_token = create_session(api_key)
        print("Session created successfully")
        
        # Step 2: Get logs using the session
        logs = get_logs(session_token)
        print("Logs retrieved successfully:")
        print(logs)
        
    except Exception as e:
        print(f"Error: {str(e)}")

def generate_api_key():
    """Generate a random API key"""
    return str(uuid.uuid4())

if __name__ == "__main__":
    # Generate and insert a new API key
    API_KEY = generate_api_key()
    USER_ID = "example_user"
    print(API_KEY)
    if not insert_api_key(API_KEY, USER_ID):
        print("Failed to insert API key")
        exit(1)
        
    try:
        # Run the example
        example_usage(API_KEY)
    finally:
        # Clean up by deleting the API key
        if not delete_api_key(API_KEY):
            print("Warning: Failed to delete API key")
