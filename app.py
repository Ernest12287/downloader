import os
import logging
from typing import Optional
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from utils.downloader import SocialDownloader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration
DEBUG = os.getenv("DEBUG", "false").lower() == "true"
PORT = int(os.getenv("PORT", 8000))  # Render provides PORT automatically

app = FastAPI(
    title="Social Media Downloader API",
    description="API for downloading content from various social media platforms",
    version="1.0.0",
    debug=DEBUG
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize downloader
downloader = SocialDownloader()

@app.get("/")
async def root():
    return {
        "message": "Social Media Downloader API",
        "version": "1.0.0",
        "endpoints": {
            "download": "/api/download?url=YOUR_URL",
            "info": "/api/info?url=YOUR_URL",
            "health": "/health"
        },
        "supported_platforms": ["DouYin", "TikTok", "Twitter", "WeiBo"]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "social-downloader-api"}

@app.get("/api/download")
async def download_content(
    url: str = Query(..., description="URL of the content to download"),
    format_type: Optional[str] = Query("info", description="Return format: info or direct")
):
    """
    Download content from social media platforms
    """
    try:
        logger.info(f"Download request for URL: {url}")
        
        result = await downloader.download_content(url)
        
        if format_type == "direct" and result.get("video_url"):
            return JSONResponse({
                "success": True,
                "direct_url": result["video_url"],
                "title": result.get("title", ""),
                "author": result.get("author", "")
            })
        
        return JSONResponse({
            "success": True,
            "data": result
        })
        
    except Exception as e:
        logger.error(f"Download error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Download failed: {str(e)}"
        )

@app.get("/api/info")
async def get_content_info(url: str = Query(..., description="URL to get info from")):
    """
    Get content information without downloading
    """
    try:
        logger.info(f"Info request for URL: {url}")
        
        info = await downloader.get_content_info(url)
        
        return JSONResponse({
            "success": True,
            "data": info
        })
        
    except Exception as e:
        logger.error(f"Info error: {str(e)}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to get info: {str(e)}"
        )

@app.get("/api/platforms")
async def get_supported_platforms():
    """
    Get list of supported platforms
    """
    return {
        "success": True,
        "platforms": [
            {
                "name": "DouYin",
                "example": "https://v.douyin.com/abc123/",
                "supported_types": ["video", "images", "live"]
            },
            {
                "name": "TikTok",
                "example": "https://www.tiktok.com/@user/video/123456",
                "supported_types": ["video", "images"]
            },
            {
                "name": "Twitter",
                "example": "https://twitter.com/user/status/123456",
                "supported_types": ["video", "images"]
            },
            {
                "name": "WeiBo",
                "example": "https://weibo.com/1234567890/abc123",
                "supported_types": ["video", "images"]
            }
        ]
    }

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0",  # Always use 0.0.0.0 for deployment
        port=PORT,        # Use PORT from environment (Render provides this)
        reload=DEBUG      # Only reload in debug mode
    )