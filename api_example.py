import requests

# Base URL of the API
BASE_URL = "http://localhost:8000"

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

if __name__ == "__main__":
    # Replace with your actual API key
    API_KEY = "your-api-key-here"
    
    # Run the example
    example_usage(API_KEY)
