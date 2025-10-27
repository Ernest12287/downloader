import asyncio
import re
from typing import Dict, Optional
import logging

# Import F2 apps properly
from f2.apps.douyin import DouyinCrawler
from f2.apps.tiktok import TiktokCrawler
from f2.apps.twitter import TwitterCrawler
from f2.apps.weibo import WeiboCrawler

logger = logging.getLogger(__name__)

class SocialDownloader:
    def __init__(self):
        self.supported_platforms = {
            'douyin': self._download_douyin,
            'tiktok': self._download_tiktok,
            'twitter': self._download_twitter,
            'weibo': self._download_weibo
        }
    
    def _detect_platform(self, url: str) -> Optional[str]:
        """Detect platform from URL"""
        patterns = {
            'douyin': [
                r'douyin\.com',
                r'iesdouyin\.com'
            ],
            'tiktok': [
                r'tiktok\.com'
            ],
            'twitter': [
                r'twitter\.com',
                r'x\.com'
            ],
            'weibo': [
                r'weibo\.com',
                r'weibo\.cn'
            ]
        }
        
        for platform, pattern_list in patterns.items():
            for pattern in pattern_list:
                if re.search(pattern, url, re.IGNORECASE):
                    return platform
        return None
    
    async def _download_douyin(self, url: str) -> Dict:
        """Download from Douyin"""
        try:
            async with DouyinCrawler() as crawler:
                # Get video info
                video_info = await crawler.fetch_one_video(url)
                
                if not video_info:
                    raise Exception("No video found")
                
                # Extract basic info
                result = {
                    'platform': 'douyin',
                    'title': getattr(video_info, 'desc', 'No title'),
                    'author': getattr(video_info.author, 'nickname', 'Unknown'),
                    'author_id': getattr(video_info.author, 'unique_id', ''),
                    'video_url': None,
                    'cover_url': None,
                }
                
                # Try to get video URL
                if hasattr(video_info, 'video'):
                    video_data = video_info.video
                    if hasattr(video_data, 'play_addr'):
                        play_addr = video_data.play_addr
                        if hasattr(play_addr, 'url_list') and play_addr.url_list:
                            result['video_url'] = play_addr.url_list[0]
                
                # Get cover URL
                if hasattr(video_info, 'video') and hasattr(video_info.video, 'cover'):
                    cover_data = video_info.video.cover
                    if hasattr(cover_data, 'url_list') and cover_data.url_list:
                        result['cover_url'] = cover_data.url_list[0]
                
                return result
                
        except Exception as e:
            logger.error(f"Douyin download error: {str(e)}")
            raise Exception(f"Douyin download failed: {str(e)}")
    
    async def _download_tiktok(self, url: str) -> Dict:
        """Download from TikTok"""
        try:
            async with TiktokCrawler() as crawler:
                video_info = await crawler.fetch_one_video(url)
                
                if not video_info:
                    raise Exception("No video found")
                
                result = {
                    'platform': 'tiktok',
                    'title': getattr(video_info, 'desc', 'No title'),
                    'author': getattr(video_info.author, 'nickname', 'Unknown'),
                    'author_id': getattr(video_info.author, 'unique_id', ''),
                    'video_url': None,
                    'cover_url': None,
                }
                
                # Get video URL
                if hasattr(video_info, 'video'):
                    video_data = video_info.video
                    if hasattr(video_data, 'play_addr'):
                        play_addr = video_data.play_addr
                        if hasattr(play_addr, 'url_list') and play_addr.url_list:
                            result['video_url'] = play_addr.url_list[0]
                
                return result
                
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}")
            raise Exception(f"TikTok download failed: {str(e)}")
    
    async def _download_twitter(self, url: str) -> Dict:
        """Download from Twitter"""
        try:
            async with TwitterCrawler() as crawler:
                tweet_info = await crawler.fetch_tweet_detail(url)
                
                if not tweet_info:
                    raise Exception("No tweet found")
                
                result = {
                    'platform': 'twitter',
                    'text': getattr(tweet_info, 'text', ''),
                    'author': getattr(tweet_info.user, 'screen_name', 'Unknown'),
                    'media_urls': []
                }
                
                # Add media extraction logic here based on tweet_info structure
                
                return result
                
        except Exception as e:
            logger.error(f"Twitter download error: {str(e)}")
            raise Exception(f"Twitter download failed: {str(e)}")
    
    async def _download_weibo(self, url: str) -> Dict:
        """Download from Weibo"""
        try:
            async with WeiboCrawler() as crawler:
                weibo_info = await crawler.fetch_weibo_detail(url)
                
                if not weibo_info:
                    raise Exception("No weibo found")
                
                result = {
                    'platform': 'weibo',
                    'text': getattr(weibo_info, 'text', ''),
                    'author': getattr(weibo_info.user, 'screen_name', 'Unknown'),
                    'media_urls': []
                }
                
                return result
                
        except Exception as e:
            logger.error(f"Weibo download error: {str(e)}")
            raise Exception(f"Weibo download failed: {str(e)}")
    
    async def download_content(self, url: str) -> Dict:
        """Main download method"""
        platform = self._detect_platform(url)
        
        if not platform:
            raise Exception("Unsupported platform or invalid URL")
        
        if platform not in self.supported_platforms:
            raise Exception(f"Platform {platform} not supported")
        
        download_func = self.supported_platforms[platform]
        return await download_func(url)
    
    async def get_content_info(self, url: str) -> Dict:
        """Get content information without downloading"""
        platform = self._detect_platform(url)
        
        if not platform:
            raise Exception("Unsupported platform or invalid URL")
        
        # For now, we'll use the same method but you can optimize this
        info = await self.download_content(url)
        
        # Remove download URLs if you want just metadata
        info.pop('video_url', None)
        info.pop('cover_url', None)
        
        return info