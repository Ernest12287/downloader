import yt_dlp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SocialDownloader:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
    
    async def download_content(self, url: str) -> Dict:
        """Download content using yt-dlp"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("No content found")
                
                result = {
                    'success': True,
                    'platform': info.get('extractor', 'unknown'),
                    'title': info.get('title', 'No title'),
                    'author': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'video_url': None,
                    'thumbnail': info.get('thumbnail'),
                }
                
                # Get the best video URL
                if 'url' in info:
                    result['video_url'] = info['url']
                elif 'formats' in info:
                    # Get the best format
                    formats = info['formats']
                    if formats:
                        result['video_url'] = formats[-1]['url']
                
                return result
                
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
    
    async def get_content_info(self, url: str) -> Dict:
        """Get content information without downloading"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise Exception("No content found")
                
                return {
                    'success': True,
                    'platform': info.get('extractor', 'unknown'),
                    'title': info.get('title', 'No title'),
                    'author': info.get('uploader', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'thumbnail': info.get('thumbnail'),
                    'view_count': info.get('view_count', 0),
                    'description': info.get('description', ''),
                }
                
        except Exception as e:
            logger.error(f"Info error: {str(e)}")
            raise Exception(f"Failed to get info: {str(e)}")