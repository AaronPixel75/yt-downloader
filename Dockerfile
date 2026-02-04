FROM python:3.11-slim

# Install dependencies including Node.js for yt-dlp JavaScript runtime
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    nodejs \
    npm \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp

# Configure yt-dlp to use nodejs
RUN mkdir -p /root/.config/yt-dlp && \
    echo "--js-runtimes nodejs" > /root/.config/yt-dlp/config

# Set working directory
WORKDIR /app

# Copy application
COPY app.py .

# Create downloads directory
RUN mkdir -p /app/downloads

# Set environment variables
ENV YT_DLP_PATH=/usr/local/bin/yt-dlp
ENV DOWNLOAD_DIR=/app/downloads
ENV PORT=8080

# Expose port
EXPOSE 8080

# Run the application
CMD ["python3", "app.py", "8080"]
