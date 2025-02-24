# app.py
import os
from fastapi import FastAPI, HTTPException, Depends
 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # Correct import, uvicorn is not in a package
from route_user import app as router_user
from backend_kali_infer import run_agent_with_prompt_addition
import sqlite3
 
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log", mode="a")  # Logs will be saved in app.log
    ]
)

logger = logging.getLogger(__name__)

 

app = FastAPI()

# Log when the application starts
logger.info("Starting FastAPI application")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routes from routes.py
try:
    app.include_router(router_user)

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

    @app.post("/start-kali-infer")
    async def start_kali_infer(additional_prompt: str):
        """
        Start the backend kali inference with additional prompt
        """
        try:
            # Clear logs before starting new job
            clear_code_logs()
            
            logger.info(f"Starting kali infer with prompt: {additional_prompt}")
            result = run_agent_with_prompt_addition(additional_prompt)
            return {"status": "success", "result": result}
        except Exception as e:
            logger.error(f"Error in kali infer: {str(e)}", exc_info=True)
            raise HTTPException(status_code=500, detail=str(e))

    @app.get("/get-logs")
    async def get_logs():
        """Get all code logs from the database"""
        try:
            conn = sqlite3.connect('agent_logs.db')
            cursor = conn.cursor()
            cursor.execute("SELECT timestamp, title, content FROM code_logs ORDER BY timestamp DESC")
            logs = cursor.fetchall()
            conn.close()
            
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


    logger.info("Successfully included routes from routes.py")
except Exception as e:
    logger.error(f"Error including routes from routes.py: {str(e)}", exc_info=True)
    raise

if __name__ == "__main__":
    try:
        logger.info("Running FastAPI application with Uvicorn")
        # Import the application string
        app_str = os.getenv("APP_STRING", "app:app")  # Example: "app:app" as a default value
        uvicorn.run(app_str, host="0.0.0.0", port=8087, workers=int(os.getenv("HG_WORKERS", 2)))
    except Exception as e:
        logger.error(f"Failed to start Uvicorn server: {str(e)}", exc_info=True)
        raise
