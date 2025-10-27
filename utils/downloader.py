import yt_dlp
import logging
from typing import Dict, Optional
import asyncio
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

class SocialDownloader:
    def __init__(self):
        self.ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        self.executor = ThreadPoolExecutor(max_workers=1)
    
    def _extract_info(self, url: str):
        """Sync function to extract info (yt-dlp is sync)"""
        try:
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                return ydl.extract_info(url, download=False)
        except Exception as e:
            logger.error(f"yt-dlp extraction error: {str(e)}")
            raise e
    
    async def download_content(self, url: str) -> Dict:
        """Download content using yt-dlp"""
        try:
            # Run yt-dlp in thread pool since it's synchronous
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self.executor, self._extract_info, url)
            
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
                'view_count': info.get('view_count', 0),
            }
            
            # Get the best video URL
            if 'url' in info:
                result['video_url'] = info['url']
            elif 'formats' in info:
                # Find the best format (usually the last one)
                formats = info['formats']
                if formats:
                    # Prefer formats with video and audio
                    best_format = None
                    for fmt in reversed(formats):
                        if fmt.get('vcodec') != 'none' and fmt.get('acodec') != 'none':
                            best_format = fmt
                            break
                    if not best_format:
                        best_format = formats[-1]
                    
                    result['video_url'] = best_format.get('url')
            
            return result
            
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            raise Exception(f"Download failed: {str(e)}")
    
    async def get_content_info(self, url: str) -> Dict:
        """Get content information without downloading"""
        try:
            loop = asyncio.get_event_loop()
            info = await loop.run_in_executor(self.executor, self._extract_info, url)
            
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
                'description': info.get('description', '')[:500],
            }
            
        except Exception as e:
            logger.error(f"Info error: {str(e)}")
            raise Exception(f"Failed to get info: {str(e)}")