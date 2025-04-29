import os
import requests
from pathlib import Path

def download_media(url: str) -> str:
    temp_dir = Path('temp_media')
    temp_dir.mkdir(exist_ok=True)
    try:
        ext = os.path.splitext(url.split('?')[0])[1] or '.jpg'
        path = temp_dir / f"{os.urandom(8).hex()}{ext}"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        
        with requests.get(url, headers=headers, stream=True, timeout=10) as r:
            r.raise_for_status()
            with open(path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return str(path)
    except Exception as e:
        if 'path' in locals() and path.exists():
            path.unlink()
        raise e

def extract_media_urls(tweet):
    photos, videos = [], []
    if hasattr(tweet, 'media'):
        for m in tweet.media:
            if m.type == 'photo':
                photos.append(m.fullUrl)
            elif m.type == 'video':
                videos.append(max(
                    (v for v in m.variants if v.contentType == 'video/mp4'),
                    key=lambda v: v.bitrate or 0
                ).url)
    return photos, videos

def cleanup_media():
    """Remove media files older than 1 hour"""
    temp_dir = Path('temp_media')
    if temp_dir.exists():
        for f in temp_dir.glob('*'):
            try:
                if f.stat().st_mtime < time.time() - 3600:
                    f.unlink()
            except:
                pass
