import os
import requests
from pathlib import Path

def download_media(url: str) -> str:
    temp_dir = Path('temp_media')
    temp_dir.mkdir(exist_ok=True)
    try:
        # Clean URL and get extension
        clean_url = url.split('?')[0]
        ext = os.path.splitext(clean_url)[1] or '.jpg'
        
        # Generate filename
        path = temp_dir / f"{os.urandom(8).hex()}{ext}"
        
        # Download with realistic headers
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
            'Referer': 'https://x.com/'
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
