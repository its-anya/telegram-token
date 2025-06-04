import aiohttp
import os
from dotenv import load_dotenv
import urllib.parse
import datetime

load_dotenv()

INSHORT_API_TOKEN = os.getenv("INSHORT_API_TOKEN")
API_BASE_URL = "https://inshorturl.com/api"

async def create_short_url(original_url, custom_alias=None):
    """Create a short URL using the InShortURL API"""
    params = {
        'api': INSHORT_API_TOKEN,
        'url': original_url
    }
    
    if custom_alias:
        params['alias'] = custom_alias
    
    # Construct the API URL
    query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
    api_url = f"{API_BASE_URL}?{query_string}"
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    result = await response.json()
                    if result.get("status") == "success":
                        return result.get("shortenedUrl")
                    else:
                        print(f"API Error: {result.get('message', 'Unknown error')}")
                        return None
                else:
                    print(f"API Request Failed: {response.status}")
                    return None
    except Exception as e:
        print(f"Error creating short URL: {str(e)}")
        return None

async def create_token_url(user_id, bot_username):
    """Create a URL that will be used for token generation with 24-hour expiration"""
    # This will be a link to your website or a direct link to the bot
    # You can customize the URL structure as needed
    original_url = f"https://t.me/{bot_username}?start=token_{user_id}"
    
    # Create a custom alias for the token URL
    custom_alias = f"token_{user_id}_{int(datetime.datetime.now().timestamp())}"
    
    try:
        # Construct the API URL with parameters
        params = {
            'api': INSHORT_API_TOKEN,
            'url': original_url,
            'alias': custom_alias
        }
        
        # Construct the API URL
        query_string = "&".join([f"{k}={urllib.parse.quote(str(v))}" for k, v in params.items()])
        api_url = f"{API_BASE_URL}?{query_string}"
        
        print(f"Calling InShortURL API: {api_url}")
        
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as response:
                if response.status == 200:
                    result = await response.json()
                    print(f"InShortURL API response: {result}")
                    if result.get("status") == "success":
                        return result.get("shortenedUrl")
                    else:
                        print(f"API Error: {result.get('message', 'Unknown error')}")
                else:
                    print(f"API Request Failed: {response.status}")
    except Exception as e:
        print(f"Error creating token URL: {str(e)}")
    
    # If API call fails, return direct Telegram URL as fallback
    return original_url

async def create_video_url(video_id, bot_username):
    """Create a permanent URL for accessing a specific video"""
    # Create a direct Telegram URL for the video
    telegram_url = f"https://t.me/{bot_username}?start=video_{video_id}"
    
    # Return the Telegram URL directly - these links never expire
    return telegram_url 