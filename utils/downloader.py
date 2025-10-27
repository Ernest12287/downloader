import asyncio
import re
from typing import Dict, Optional
import logging
from f2.apps.douyin import API as DouyinAPI
from f2.apps.tiktok import API as TiktokAPI
from f2.apps.twitter import API as TwitterAPI
from f2.apps.weibo import API as WeiboAPI

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
                r'douyin\.com',
                r'iesdouyin\.com'
            ],
            'tiktok': [
                r'tiktok\.com',
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
            video_info = await DouyinAPI.fetch_one_video(url)
            
            if not video_info or not hasattr(video_info, 'aweme_list') or not video_info.aweme_list:
                raise Exception("No video found")
            
            aweme = video_info.aweme_list[0]
            result = {
                'platform': 'douyin',
                'title': getattr(aweme, 'desc', 'No title'),
                'author': getattr(aweme.author, 'nickname', 'Unknown'),
                'author_id': getattr(aweme.author, 'unique_id', ''),
                'video_url': None,
                'cover_url': None,
                'duration': getattr(aweme.video, 'duration', 0) if hasattr(aweme, 'video') else 0,
                'created_at': getattr(aweme, 'create_time', 0)
            }
            
            # Get video URL
            if hasattr(aweme, 'video'):
                video_addr = getattr(aweme.video, 'play_addr', None)
                if video_addr and hasattr(video_addr, 'url_list') and video_addr.url_list:
                    result['video_url'] = video_addr.url_list[0]
            
            # Get cover URL
            if hasattr(aweme, 'video') and hasattr(aweme.video, 'cover'):
                cover_urls = getattr(aweme.video.cover, 'url_list', [])
                if cover_urls:
                    result['cover_url'] = cover_urls[0]
            
            return result
            
        except Exception as e:
            logger.error(f"Douyin download error: {str(e)}")
            raise Exception(f"Douyin download failed: {str(e)}")
    
    async def _download_tiktok(self, url: str) -> Dict:
        """Download from TikTok"""
        try:
            video_info = await TiktokAPI.fetch_one_video(url)
            
            if not video_info or not hasattr(video_info, 'aweme_list') or not video_info.aweme_list:
                raise Exception("No video found")
            
            aweme = video_info.aweme_list[0]
            result = {
                'platform': 'tiktok',
                'title': getattr(aweme, 'desc', 'No title'),
                'author': getattr(aweme.author, 'nickname', 'Unknown'),
                'author_id': getattr(aweme.author, 'unique_id', ''),
                'video_url': None,
                'cover_url': None
            }
            
            # Get video URL (TikTok structure might be different)
            if hasattr(aweme, 'video'):
                video_addr = getattr(aweme.video, 'play_addr', None)
                if video_addr and hasattr(video_addr, 'url_list') and video_addr.url_list:
                    result['video_url'] = video_addr.url_list[0]
            
            return result
            
        except Exception as e:
            logger.error(f"TikTok download error: {str(e)}")
            raise Exception(f"TikTok download failed: {str(e)}")
    
    async def _download_twitter(self, url: str) -> Dict:
        """Download from Twitter"""
        try:
            tweet_info = await TwitterAPI.fetch_tweet_detail(url)
            
            if not tweet_info:
                raise Exception("No tweet found")
            
            result = {
                'platform': 'twitter',
                'text': getattr(tweet_info, 'text', ''),
                'author': getattr(tweet_info.user, 'screen_name', 'Unknown'),
                'media_urls': []
            }
            
            # Extract media URLs (implementation depends on Twitter API response)
            # This is a simplified version
            
            return result
            
        except Exception as e:
            logger.error(f"Twitter download error: {str(e)}")
            raise Exception(f"Twitter download failed: {str(e)}")
    
    async def _download_weibo(self, url: str) -> Dict:
        """Download from Weibo"""
        try:
            weibo_info = await WeiboAPI.fetch_weibo_detail(url)
            
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