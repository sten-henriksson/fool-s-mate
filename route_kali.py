from fastapi import APIRouter, Depends, HTTPException, Header, Cookie, Response
from datetime import timedelta
from quaries_user import create_access_token, SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import jwt, JWTError
from quaries_user import verify_api_key, insert_api_key, delete_api_key
import logging

logger = logging.getLogger(__name__)

router = APIRouter()

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
