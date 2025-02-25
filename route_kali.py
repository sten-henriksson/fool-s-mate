from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Header, Cookie, Response
from pydantic import BaseModel
from datetime import timedelta
from quaries_user import create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError
from quaries_user import verify_api_key, insert_api_key, delete_api_key
from backend_kali_infer import kali_infer
import logging
import sqlite3

logger = logging.getLogger(__name__)

router = APIRouter()

def verify_session_token(session_token: str) -> str:
    """Verify session token and return API key if valid"""
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        api_key: str = payload.get("sub")
        if api_key is None or not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid session token")
        return api_key
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")

def clear_code_logs():
    """Clear all entries from the code_logs table"""
    try:
        conn = sqlite3.connect('agent_logs.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM code_logs")
        conn.commit()
        conn.close()
        logger.info("Cleared code logs")
    except sqlite3.OperationalError as e:
        logger.error(f"Error clearing code logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

class KaliInferRequest(BaseModel):
    additional_prompt: str

@router.post("/start-kali-infer")
async def start_kali_infer(
    request: KaliInferRequest,
    session_token: str = Cookie(None)
):
    """
    Start the backend kali inference with additional prompt
    Requires valid session cookie
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    
    try:
        # Verify session token
        verify_session_token(session_token)
        
        # Clear logs before starting new job
        clear_code_logs()
        
        logger.info(f"Starting kali infer with prompt: {request.additional_prompt}")
        
        # Run the agent using the KaliInfer instance and get the result
        result = kali_infer.run_agent_with_prompt_addition(request.additional_prompt)
        
        # Return the result in a structured format
        return {
            "status": "success",
            "result": {
                "output": result,
                "prompt": request.additional_prompt
            }
        }
    except HTTPException:
        raise  # Re-raise HTTP exceptions
    except Exception as e:
        logger.error(f"Error in kali infer: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Error running kali inference: {str(e)}"
        )

@router.get("/get-logs", response_model=Dict[str, Any])
async def get_logs(session_token: str = Cookie(None)) -> Dict[str, Any]:
    """
    Get all code logs from the database
    Requires valid session cookie
    
    Returns:
        Dict[str, Any]: Dictionary containing status and logs
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        api_key: str = payload.get("sub")
        if api_key is None or not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid session token")
            
         
        with sqlite3.connect('agent_logs.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, title, content FROM code_logs ORDER BY timestamp DESC")
            logs = cursor.fetchall()
            
            # Format logs for response
            formatted_logs = []
            for log in logs:
                timestamp, title, content = log
                formatted_logs.append({
                    "timestamp": timestamp,
                    "title": title,
                    "content": content
                })
            
            return {"status": "success", "logs": formatted_logs}
    except sqlite3.OperationalError as e:
        logger.error(f"Error fetching logs: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api-keys/verify")
async def verify_key(api_key: str = Header(..., description="API Key to verify")):
    """
    Verify if an API key is valid
    """
    try:
        if verify_api_key(api_key):
            return {"status": "success", "message": "API key is valid"}
        raise HTTPException(status_code=401, detail="Invalid API key")
    except Exception as e:
        logger.error(f"Error verifying API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api-keys")
async def create_key(user_id: str, api_key: str = Header(..., description="New API key to create")):
    """
    Create a new API key for a user
    """
    try:
        if insert_api_key(api_key, user_id):
            return {"status": "success", "message": "API key created"}
        raise HTTPException(status_code=409, detail="API key already exists")
    except Exception as e:
        logger.error(f"Error creating API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.delete("/api-keys")
async def remove_key(api_key: str = Header(..., description="API key to delete")):
    """
    Delete an existing API key
    """
    try:
        if delete_api_key(api_key):
            return {"status": "success", "message": "API key deleted"}
        raise HTTPException(status_code=404, detail="API key not found")
    except Exception as e:
        logger.error(f"Error deleting API key: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.post("/api-keys/session")
async def create_session(api_key: str = Header(..., description="API Key to create session")):
    """
    Create a JWT session cookie using an API key
    """
    try:
        if not verify_api_key(api_key):
            raise HTTPException(status_code=401, detail="Invalid API key")
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": api_key}, expires_delta=access_token_expires
        )
        
        response = Response(content="Session created")
        response.set_cookie(
            key="session_token",
            value=access_token,
            httponly=True,
            max_age=ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            secure=True,  # Set to False for development without HTTPS
            samesite="lax"
        )
        return response
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/api-keys/verify-session")
async def verify_session(session_token: str = Cookie(None)):
    """
    Verify if the session cookie is valid
    """
    if not session_token:
        raise HTTPException(status_code=401, detail="No session token provided")
    
    try:
        payload = jwt.decode(session_token, SECRET_KEY, algorithms=[ALGORITHM])
        api_key: str = payload.get("sub")
        if api_key is None:
            raise HTTPException(status_code=401, detail="Invalid session token")
        
        if verify_api_key(api_key):
            return {"status": "success", "message": "Valid session"}
        raise HTTPException(status_code=401, detail="Invalid session token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid session token")
    except Exception as e:
        logger.error(f"Error verifying session: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal server error")
