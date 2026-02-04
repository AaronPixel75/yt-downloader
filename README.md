# YT Downloader Pro

A web-based YouTube video downloader with automatic cloud upload for sharing.

## Features
- 🎬 Download from YouTube, TikTok, Instagram, Twitter + 1000 sites
- 🎵 Audio extraction (MP3)
- 📐 Quality selection (360p-1080p)
- 🔗 Auto-upload to cloud for shareable links
- 📱 Mobile-friendly UI

## Deploy to Railway (One Click)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/yt-downloader)

Or manually:
1. Fork this repo
2. Connect to Railway
3. Deploy!

## Run Locally

```bash
# Install yt-dlp
curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o ~/.local/bin/yt-dlp
chmod +x ~/.local/bin/yt-dlp

# Run the app
python3 app.py

# Open http://localhost:8888
```

## Docker

```bash
docker build -t yt-downloader .
docker run -p 8080:8080 yt-downloader
```

## License
MIT
