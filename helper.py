import os
import requests
from pathlib import Path

def download_media(url: str) -> str:
    temp_dir = Path('temp_media')
    temp_dir.mkdir(exist_ok=True)
    try:
        ext = os.path.splitext(url)[1] or '.jpg'
        path = temp_dir / f"{os.urandom(8).hex()}{ext}"
        with requests.get(url, stream=True, timeout=10) as r:
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
