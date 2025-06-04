# Telegram Video Bot with Token System

This Telegram bot allows users to access videos via short links after refreshing their token by passing through an ad link. The token is valid for 24 hours.

## Features

- Token-based access system (24-hour validity)
- Admin panel for uploading videos
- Short URL generation for videos
- Channel integration (auto-detects and saves videos posted in channels)
- Secure video access
- Premium membership (ad-free access)
- Channel join enforcement for users
- QR code/UPI payment for premium

## Setup Instructions

### Prerequisites

- Python 3.7 or higher
- A Telegram Bot API token (create via @BotFather)
- An InShortURL API token

### Installation

1. Clone this repository
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Update the `.env` file with your credentials:

```
TELEGRAM_BOT_TOKEN=your_bot_token
INSHORT_API_TOKEN=your_inshort_api_token
ADMIN_USER_IDS=your_telegram_user_id
```

> Note: To get your Telegram user ID, send a message to @userinfobot on Telegram.

4. Run the bot:

```bash
python bot.py
```

## Usage

### Admin Commands

- `/start` - Start the bot
- `/add_video` - Start the process of adding a new video
- `/list_videos` - Show all videos in the database
- `/add_channel [channel_id] [name]` - Add a channel
- `/list_channels` - List all channels
- `/add_premium [user_id] [months]` - Add premium access to a user
- `/remove_premium [user_id]` - Remove premium access from a user
- `/list_premium` - List all premium users
- `/setup_special_channel` - Add the special channel (ID: -1002602136007) to the bot
- `/help` - Show help message

### User Commands

- `/start` - Start the bot and check token status
- `/help` - Show help message

## How It Works

1. Users must join required channels to use the bot
2. Users must refresh their token by clicking the "Refresh Token" button and passing through an ad
3. After refreshing the token, users can access videos for 24 hours
4. Admins can upload videos and share links
5. Videos posted in registered channels are automatically saved and get a short link
6. Premium users can access videos without ads or token restrictions

## Premium Membership

- Users can purchase premium via UPI/QR code (see in-bot instructions)
- Premium removes all ads and token restrictions

## Troubleshooting

- If you encounter any issues with short URL generation, check your InShortURL API token
- Make sure your bot has admin privileges in the channels you add
- Ensure your Telegram Bot has a valid token
- Use `/list_channels` to see if your channel is registered
- Use `/setup_special_channel` if your channel is not listed

## Customization

You can customize the token duration by modifying the `set_user_token` function in the `database_json.py` file.
