# app.py
import os
from fastapi import FastAPI, HTTPException, Depends
 
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # Correct import, uvicorn is not in a package
 
from route_kali import router as router_kali
 
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
    app.include_router(router_kali)


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
