#!/usr/bin/env python3
"""
YouTube Downloader & Share - Full Web Application
Downloads videos and automatically uploads to file sharing
"""

import subprocess
import os
import re
import json
import tempfile
import shutil
from http.server import HTTPServer, SimpleHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import threading
import time

DOWNLOAD_DIR = os.environ.get('DOWNLOAD_DIR', os.path.expanduser("~/Downloads/YouTube"))
YT_DLP_PATH = os.environ.get('YT_DLP_PATH', os.path.expanduser("~/.local/bin/yt-dlp"))

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

HTML_PAGE = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>YT Downloader Pro</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Inter', sans-serif;
            background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }
        
        .container {
            background: rgba(255, 255, 255, 0.05);
            backdrop-filter: blur(20px);
            border-radius: 24px;
            padding: 50px;
            max-width: 650px;
            width: 100%;
            box-shadow: 0 25px 50px rgba(0, 0, 0, 0.5);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .logo {
            text-align: center;
            font-size: 5em;
            margin-bottom: 10px;
            animation: pulse 2s infinite;
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        h1 {
            color: #fff;
            text-align: center;
            margin-bottom: 8px;
            font-size: 2.2em;
            font-weight: 700;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d, #6bcb77, #4d96ff);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-size: 300% 300%;
            animation: gradient 5s ease infinite;
        }
        
        @keyframes gradient {
            0% { background-position: 0% 50%; }
            50% { background-position: 100% 50%; }
            100% { background-position: 0% 50%; }
        }
        
        .subtitle {
            color: rgba(255, 255, 255, 0.6);
            text-align: center;
            margin-bottom: 35px;
            font-size: 1em;
        }
        
        .features {
            display: flex;
            justify-content: center;
            gap: 20px;
            margin-bottom: 30px;
            flex-wrap: wrap;
        }
        
        .feature {
            background: rgba(255, 255, 255, 0.08);
            padding: 10px 18px;
            border-radius: 50px;
            font-size: 12px;
            color: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(255, 255, 255, 0.1);
        }
        
        .input-group {
            margin-bottom: 25px;
        }
        
        label {
            color: rgba(255, 255, 255, 0.9);
            display: block;
            margin-bottom: 10px;
            font-weight: 500;
            font-size: 14px;
        }
        
        input[type="text"] {
            width: 100%;
            padding: 18px 24px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.08);
            font-size: 16px;
            color: #fff;
            outline: none;
            transition: all 0.3s ease;
        }
        
        input[type="text"]::placeholder {
            color: rgba(255, 255, 255, 0.4);
        }
        
        input[type="text"]:focus {
            border-color: #ff6b6b;
            box-shadow: 0 0 30px rgba(255, 107, 107, 0.2);
        }
        
        .options-row {
            display: flex;
            gap: 15px;
            margin-bottom: 25px;
        }
        
        .option-group {
            flex: 1;
        }
        
        select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.08);
            font-size: 14px;
            color: #fff;
            outline: none;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        
        select:focus {
            border-color: #4d96ff;
        }
        
        select option {
            background: #1a1a2e;
            color: #fff;
        }
        
        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 25px;
            padding: 16px 20px;
            background: rgba(107, 203, 119, 0.1);
            border-radius: 12px;
            border: 1px solid rgba(107, 203, 119, 0.3);
        }
        
        .checkbox-group input[type="checkbox"] {
            width: 22px;
            height: 22px;
            accent-color: #6bcb77;
            cursor: pointer;
        }
        
        .checkbox-group label {
            margin: 0;
            color: #6bcb77;
            cursor: pointer;
        }
        
        .download-btn {
            width: 100%;
            padding: 20px;
            background: linear-gradient(135deg, #ff6b6b 0%, #ff8e53 100%);
            border: none;
            border-radius: 14px;
            color: #fff;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 2px;
            position: relative;
            overflow: hidden;
        }
        
        .download-btn::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
            transition: left 0.5s;
        }
        
        .download-btn:hover::before {
            left: 100%;
        }
        
        .download-btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 15px 40px rgba(255, 107, 107, 0.4);
        }
        
        .download-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 30px;
            padding: 25px;
            border-radius: 16px;
            background: rgba(0, 0, 0, 0.3);
            color: #fff;
            display: none;
            font-size: 14px;
            line-height: 1.6;
        }
        
        .status.show {
            display: block;
            animation: fadeIn 0.3s ease;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .status.success {
            border: 1px solid rgba(107, 203, 119, 0.5);
            background: rgba(107, 203, 119, 0.1);
        }
        
        .status.error {
            border: 1px solid rgba(255, 107, 107, 0.5);
            background: rgba(255, 107, 107, 0.1);
        }
        
        .status.loading {
            border: 1px solid rgba(77, 150, 255, 0.5);
            background: rgba(77, 150, 255, 0.1);
        }
        
        .spinner {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,.3);
            border-radius: 50%;
            border-top-color: #fff;
            animation: spin 1s ease-in-out infinite;
            margin-right: 12px;
            vertical-align: middle;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
        
        .link-box {
            background: rgba(0, 0, 0, 0.4);
            padding: 15px 20px;
            border-radius: 10px;
            margin-top: 15px;
            word-break: break-all;
            display: flex;
            align-items: center;
            gap: 10px;
        }
        
        .link-box a {
            color: #4d96ff;
            text-decoration: none;
            flex: 1;
        }
        
        .link-box a:hover {
            text-decoration: underline;
        }
        
        .copy-btn {
            background: #4d96ff;
            border: none;
            padding: 10px 16px;
            border-radius: 8px;
            color: #fff;
            cursor: pointer;
            font-size: 12px;
            font-weight: 600;
            transition: all 0.2s;
        }
        
        .copy-btn:hover {
            background: #3a7bd5;
        }
        
        .progress-bar {
            width: 100%;
            height: 6px;
            background: rgba(255, 255, 255, 0.1);
            border-radius: 3px;
            margin-top: 15px;
            overflow: hidden;
        }
        
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #ff6b6b, #ffd93d);
            border-radius: 3px;
            width: 0%;
            transition: width 0.3s ease;
        }
        
        .footer {
            text-align: center;
            margin-top: 30px;
            color: rgba(255, 255, 255, 0.4);
            font-size: 12px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="logo">🎬</div>
        <h1>YT Downloader Pro</h1>
        <p class="subtitle">Download & Share videos instantly</p>
        
        <div class="features">
            <span class="feature">📺 YouTube</span>
            <span class="feature">🐦 Twitter</span>
            <span class="feature">📸 Instagram</span>
            <span class="feature">🎵 TikTok</span>
            <span class="feature">+1000 sites</span>
        </div>
        
        <div class="input-group">
            <label>🔗 Video URL</label>
            <input type="text" id="url" placeholder="Paste video URL here...">
        </div>
        
        <div class="options-row">
            <div class="option-group">
                <label>📁 Format</label>
                <select id="format">
                    <option value="video">🎬 Video (MP4)</option>
                    <option value="audio">🎵 Audio (MP3)</option>
                    <option value="best">⭐ Best Quality</option>
                </select>
            </div>
            <div class="option-group">
                <label>📐 Quality</label>
                <select id="quality">
                    <option value="best">Best Available</option>
                    <option value="1080">1080p HD</option>
                    <option value="720" selected>720p</option>
                    <option value="480">480p</option>
                    <option value="360">360p</option>
                </select>
            </div>
        </div>
        
        <div class="checkbox-group">
            <input type="checkbox" id="shareLink" checked>
            <label for="shareLink">🔗 Generate shareable link (upload to cloud)</label>
        </div>
        
        <button class="download-btn" id="downloadBtn">
            🚀 Download Now
        </button>
        
        <div class="status" id="status">
            <div class="progress-bar"><div class="progress-fill" id="progress"></div></div>
        </div>
        
        <div class="footer">
            Powered by yt-dlp • Made with ❤️
        </div>
    </div>
    
    <script>
        const btn = document.getElementById('downloadBtn');
        const status = document.getElementById('status');
        const progress = document.getElementById('progress');
        
        btn.addEventListener('click', async () => {
            const url = document.getElementById('url').value.trim();
            const format = document.getElementById('format').value;
            const quality = document.getElementById('quality').value;
            const shareLink = document.getElementById('shareLink').checked;
            
            if (!url) {
                showStatus('error', '❌ Please enter a URL');
                return;
            }
            
            btn.disabled = true;
            btn.innerHTML = '<span class="spinner"></span> Processing...';
            showStatus('loading', '<span class="spinner"></span> Starting download...');
            progress.style.width = '10%';
            
            try {
                const response = await fetch('/download', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({url, format, quality, shareLink})
                });
                
                const data = await response.json();
                progress.style.width = '100%';
                
                if (data.success) {
                    let html = `✅ <strong>Download Complete!</strong><br><br>`;
                    html += `📁 File: <strong>${data.filename}</strong><br>`;
                    html += `💾 Saved to: ${data.path}`;
                    
                    if (data.shareUrl) {
                        html += `<div class="link-box">
                            <a href="${data.shareUrl}" target="_blank">${data.shareUrl}</a>
                            <button class="copy-btn" onclick="copyLink('${data.shareUrl}')">📋 Copy</button>
                        </div>`;
                    }
                    
                    showStatus('success', html);
                } else {
                    showStatus('error', `❌ Error: ${data.error}`);
                }
            } catch (err) {
                showStatus('error', `❌ Connection error: ${err.message}`);
            }
            
            btn.disabled = false;
            btn.innerHTML = '🚀 Download Now';
        });
        
        function showStatus(type, html) {
            status.className = `status show ${type}`;
            status.innerHTML = html + '<div class="progress-bar"><div class="progress-fill" id="progress"></div></div>';
        }
        
        function copyLink(url) {
            navigator.clipboard.writeText(url);
            event.target.textContent = '✓ Copied!';
            setTimeout(() => event.target.textContent = '📋 Copy', 2000);
        }
        
        document.getElementById('url').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') btn.click();
        });
        
        // Hide quality for audio
        document.getElementById('format').addEventListener('change', (e) => {
            document.getElementById('quality').parentElement.style.display = 
                e.target.value === 'audio' ? 'none' : 'block';
        });
    </script>
</body>
</html>
'''

class DownloadHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/' or self.path == '/index.html':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())
        elif self.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/download':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            data = json.loads(post_data.decode())
            
            url = data.get('url', '')
            format_type = data.get('format', 'video')
            quality = data.get('quality', '720')
            share_link = data.get('shareLink', False)
            
            result = self.download_and_share(url, format_type, quality, share_link)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            self.wfile.write(json.dumps(result).encode())
        else:
            self.send_error(404)
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def download_and_share(self, url, format_type, quality, share_link):
        try:
            # Build yt-dlp command
            cmd = [YT_DLP_PATH]
            
            if format_type == 'audio':
                cmd.extend(['-x', '--audio-format', 'mp3'])
                output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
            elif format_type == 'best':
                cmd.extend(['-f', 'bestvideo+bestaudio/best'])
                output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
            else:
                if quality == 'best':
                    cmd.extend(['-f', 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'])
                else:
                    cmd.extend(['-f', f'bestvideo[height<={quality}][ext=mp4]+bestaudio[ext=m4a]/best[height<={quality}][ext=mp4]/best'])
                output_template = os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s')
            
            cmd.extend([
                '--merge-output-format', 'mp4',
                '-o', output_template,
                '--no-playlist',
                '--print', 'after_move:filepath',
                url
            ])
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode != 0:
                return {'success': False, 'error': result.stderr or 'Download failed'}
            
            filepath = result.stdout.strip().split('\n')[-1]
            filename = os.path.basename(filepath)
            
            share_url = None
            if share_link and os.path.exists(filepath):
                share_url = self.upload_to_catbox(filepath)
            
            return {
                'success': True,
                'filename': filename,
                'path': DOWNLOAD_DIR,
                'shareUrl': share_url
            }
            
        except subprocess.TimeoutExpired:
            return {'success': False, 'error': 'Download timed out (10 min limit)'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def upload_to_catbox(self, filepath):
        try:
            result = subprocess.run([
                'curl', '-sS',
                '-F', 'reqtype=fileupload',
                '-F', f'fileToUpload=@{filepath}',
                'https://catbox.moe/user/api.php'
            ], capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0 and result.stdout.startswith('http'):
                return result.stdout.strip()
            return None
        except:
            return None
    
    def log_message(self, format, *args):
        print(f"[{self.log_date_time_string()}] {format % args}")

def run_server(port=8888):
    server = HTTPServer(('0.0.0.0', port), DownloadHandler)
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║                  🎬 YT Downloader Pro                        ║
╠══════════════════════════════════════════════════════════════╣
║  Server running at: http://localhost:{port}                   ║
║  Downloads folder:  {DOWNLOAD_DIR}         ║
║                                                              ║
║  Press Ctrl+C to stop                                        ║
╚══════════════════════════════════════════════════════════════╝
""")
    server.serve_forever()

if __name__ == '__main__':
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8888
    run_server(port)
