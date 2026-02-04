FROM python:3.11-slim

# Install dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install yt-dlp
RUN curl -L https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp -o /usr/local/bin/yt-dlp \
    && chmod +x /usr/local/bin/yt-dlp

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
