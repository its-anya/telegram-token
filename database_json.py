import os
import json
import datetime
import asyncio
from typing import List, Dict, Any, Optional, Tuple

# JSON file paths
USERS_FILE = "users.json"
VIDEOS_FILE = "videos.json"
CHANNELS_FILE = "channels.json"

# File locks to prevent concurrent writes
users_lock = asyncio.Lock()
videos_lock = asyncio.Lock()
channels_lock = asyncio.Lock()

# Helper functions to read and write JSON files
async def _read_json_file(file_path: str, default_value: Any = None) -> Any:
    """Read data from a JSON file"""
    if not os.path.exists(file_path):
        return default_value or {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    except (json.JSONDecodeError, FileNotFoundError):
        return default_value or {}

async def _write_json_file(file_path: str, data: Any) -> None:
    """Write data to a JSON file"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, indent=2, ensure_ascii=False)

# Initialize the database files
async def init_db() -> None:
    """Initialize the JSON database files if they don't exist"""
    # Create users.json if it doesn't exist
    if not os.path.exists(USERS_FILE):
        await _write_json_file(USERS_FILE, {"users": []})
    
    # Create videos.json if it doesn't exist
    if not os.path.exists(VIDEOS_FILE):
        await _write_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
    
    # Create channels.json if it doesn't exist
    if not os.path.exists(CHANNELS_FILE):
        await _write_json_file(CHANNELS_FILE, {"channels": []})

# User related functions
async def add_user(user_id: int, username: str) -> None:
    """Add a new user or update existing user"""
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        # Check if user already exists
        for user in users:
            if user["user_id"] == user_id:
                user["username"] = username
                break
        else:
            # User doesn't exist, add new user
            users.append({
                "user_id": user_id,
                "username": username,
                "token_expiry": None,
                "is_active": False
            })
        
        await _write_json_file(USERS_FILE, data)

async def set_user_token(user_id: int, hours: int = 24) -> None:
    """Set or refresh user token"""
    expiry = (datetime.datetime.now() + datetime.timedelta(hours=hours)).isoformat()
    
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        for user in users:
            if user["user_id"] == user_id:
                user["token_expiry"] = expiry
                user["is_active"] = True
                break
        else:
            # User doesn't exist, add new user with token
            users.append({
                "user_id": user_id,
                "username": None,
                "token_expiry": expiry,
                "is_active": True
            })
        
        await _write_json_file(USERS_FILE, data)

async def check_user_token(user_id: int) -> bool:
    """Check if user has a valid token"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    for user in users:
        if user["user_id"] == user_id:
            if not user["token_expiry"]:
                return False
            
            expiry = datetime.datetime.fromisoformat(user["token_expiry"])
            return datetime.datetime.now() < expiry
    
    return False

async def get_token_expiry(user_id: int) -> Optional[datetime.datetime]:
    """Get token expiry time for a user"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    for user in users:
        if user["user_id"] == user_id:
            if not user["token_expiry"]:
                return None
            
            return datetime.datetime.fromisoformat(user["token_expiry"])
    
    return None

async def set_user_joined_channels(user_id: int) -> None:
    """Mark that a user has joined the required channels"""
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        for user in users:
            if user["user_id"] == user_id:
                user["joined_channels"] = True
                break
        else:
            # User doesn't exist, add new user with joined_channels flag
            users.append({
                "user_id": user_id,
                "username": None,
                "token_expiry": None,
                "is_active": False,
                "joined_channels": True
            })
        
        await _write_json_file(USERS_FILE, data)

async def check_user_joined_channels(user_id: int) -> bool:
    """Check if user has already joined the required channels"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    for user in users:
        if user["user_id"] == user_id:
            return user.get("joined_channels", False)
    
    return False

async def set_user_premium(user_id: int, months: int = 1) -> None:
    """Set or extend premium subscription for a user"""
    expiry = (datetime.datetime.now() + datetime.timedelta(days=months*30)).isoformat()
    
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        for user in users:
            if user["user_id"] == user_id:
                # If user already has premium, extend it
                if "premium_expiry" in user and user["premium_expiry"]:
                    try:
                        current_expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
                        # Only extend if current premium is still valid
                        if current_expiry > datetime.datetime.now():
                            expiry = (current_expiry + datetime.timedelta(days=months*30)).isoformat()
                    except (ValueError, TypeError):
                        pass
                
                user["premium_expiry"] = expiry
                user["is_premium"] = True
                # Always set token to valid when giving premium
                user["token_expiry"] = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
                break
        else:
            # User doesn't exist, add new user with premium
            users.append({
                "user_id": user_id,
                "username": None,
                "token_expiry": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "is_active": True,
                "premium_expiry": expiry,
                "is_premium": True
            })
        
        await _write_json_file(USERS_FILE, data)

async def remove_user_premium(user_id: int) -> bool:
    """Remove premium status from a user"""
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        for user in users:
            if user["user_id"] == user_id:
                user["is_premium"] = False
                user["premium_expiry"] = None
                await _write_json_file(USERS_FILE, data)
                return True
        
        return False

async def check_user_premium(user_id: int) -> bool:
    """Check if user has a valid premium subscription"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    for user in users:
        if user["user_id"] == user_id:
            # First check if premium flag is set
            if not user.get("is_premium", False):
                return False
            
            # Then check expiry
            if not user.get("premium_expiry"):
                return False
            
            try:
                expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
                return datetime.datetime.now() < expiry
            except (ValueError, TypeError):
                return False
    
    return False

async def get_premium_expiry(user_id: int) -> Optional[datetime.datetime]:
    """Get premium expiry time for a user"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    for user in users:
        if user["user_id"] == user_id:
            if not user.get("premium_expiry"):
                return None
            
            try:
                return datetime.datetime.fromisoformat(user["premium_expiry"])
            except (ValueError, TypeError):
                return None
    
    return None

async def get_premium_users() -> List[Tuple[int, str, datetime.datetime]]:
    """Get all premium users with their expiry dates"""
    data = await _read_json_file(USERS_FILE, {"users": []})
    users = data["users"]
    
    premium_users = []
    for user in users:
        if user.get("is_premium", False) and user.get("premium_expiry"):
            try:
                expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
                if datetime.datetime.now() < expiry:
                    premium_users.append((
                        user["user_id"], 
                        user.get("username", "Unknown"), 
                        expiry
                    ))
            except (ValueError, TypeError):
                continue
    
    return premium_users

async def set_user_premium_days(user_id: int, days: int = 30) -> None:
    """Set or extend premium subscription for a user using days instead of months"""
    expiry = (datetime.datetime.now() + datetime.timedelta(days=days)).isoformat()
    
    async with users_lock:
        data = await _read_json_file(USERS_FILE, {"users": []})
        users = data["users"]
        
        for user in users:
            if user["user_id"] == user_id:
                # If user already has premium, extend it
                if "premium_expiry" in user and user["premium_expiry"]:
                    try:
                        current_expiry = datetime.datetime.fromisoformat(user["premium_expiry"])
                        # Only extend if current premium is still valid
                        if current_expiry > datetime.datetime.now():
                            expiry = (current_expiry + datetime.timedelta(days=days)).isoformat()
                    except (ValueError, TypeError):
                        pass
                
                user["premium_expiry"] = expiry
                user["is_premium"] = True
                # Always set token to valid when giving premium
                user["token_expiry"] = (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat()
                break
        else:
            # User doesn't exist, add new user with premium
            users.append({
                "user_id": user_id,
                "username": None,
                "token_expiry": (datetime.datetime.now() + datetime.timedelta(days=365)).isoformat(),
                "is_active": True,
                "premium_expiry": expiry,
                "is_premium": True
            })
        
        await _write_json_file(USERS_FILE, data)

# Video related functions
async def add_video(title: str, file_id: str, added_by: int, short_url: Optional[str] = None) -> int:
    """Add a new video to the database"""
    async with videos_lock:
        data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
        videos = data["videos"]
        video_id = data["next_id"]
        
        # Add new video with URL creation timestamp
        videos.append({
            "id": video_id,
            "title": title,
            "file_id": file_id,
            "short_url": short_url,
            "added_by": added_by,
            "added_on": datetime.datetime.now().isoformat(),
            "url_created_at": datetime.datetime.now().isoformat()  # Track when URL was created
        })
        
        # Increment the next ID
        data["next_id"] = video_id + 1
        
        await _write_json_file(VIDEOS_FILE, data)
        return video_id

async def update_video_url(video_id: int, short_url: str) -> None:
    """Update the short URL for a video"""
    async with videos_lock:
        data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
        videos = data["videos"]
        
        for video in videos:
            if video["id"] == video_id:
                video["short_url"] = short_url
                video["url_created_at"] = datetime.datetime.now().isoformat()  # Update URL creation time
                break
        
        await _write_json_file(VIDEOS_FILE, data)

async def check_video_url_expired(video_id: int) -> bool:
    """Check if a video URL has expired (older than 24 hours)"""
    data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
    videos = data["videos"]
    
    for video in videos:
        if video["id"] == video_id:
            if "url_created_at" not in video:
                return False
            
            created_at = datetime.datetime.fromisoformat(video["url_created_at"])
            # Check if the URL is older than 24 hours
            return (datetime.datetime.now() - created_at) > datetime.timedelta(hours=24)
    
    # If video not found, consider expired
    return True

async def refresh_video_url(video_id: int) -> None:
    """Refresh the URL creation timestamp for a video"""
    async with videos_lock:
        data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
        videos = data["videos"]
        
        for video in videos:
            if video["id"] == video_id:
                video["url_created_at"] = datetime.datetime.now().isoformat()
                break
        
        await _write_json_file(VIDEOS_FILE, data)

async def get_video_by_id(video_id: int) -> Optional[Tuple[int, str, str, str]]:
    """Get video by its ID"""
    data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
    videos = data["videos"]
    
    for video in videos:
        if video["id"] == video_id:
            return (video["id"], video["title"], video["file_id"], video["short_url"])
    
    return None

async def get_all_videos() -> List[Tuple[int, str, str, str]]:
    """Get all videos"""
    data = await _read_json_file(VIDEOS_FILE, {"videos": [], "next_id": 1})
    videos = data["videos"]
    
    # Sort videos by added_on date (newest first)
    videos.sort(key=lambda x: x.get("added_on", ""), reverse=True)
    
    return [(video["id"], video["title"], video["file_id"], video.get("short_url", "")) for video in videos]

# Channel related functions
async def add_channel(channel_id: int, title: str, added_by: int) -> None:
    """Add a new channel"""
    async with channels_lock:
        data = await _read_json_file(CHANNELS_FILE, {"channels": []})
        channels = data["channels"]
        
        # Check if channel already exists
        for channel in channels:
            if channel["channel_id"] == channel_id:
                channel["title"] = title
                break
        else:
            # Channel doesn't exist, add it
            channels.append({
                "channel_id": channel_id,
                "title": title,
                "added_by": added_by,
                "added_on": datetime.datetime.now().isoformat()
            })
        
        await _write_json_file(CHANNELS_FILE, data)

async def get_channels() -> List[Tuple[int, str]]:
    """Get all channels"""
    data = await _read_json_file(CHANNELS_FILE, {"channels": []})
    channels = data["channels"]
    
    return [(channel["channel_id"], channel["title"]) for channel in channels] 