from urllib.parse import urlparse, parse_qs

class UrlHelper:

    @staticmethod
    def fetch_youtube_id(request) -> str | None:
        """
        Extracts YouTube video ID from various URL formats.
        Returns None if not a valid YouTube URL.
        """
        data = request.get_json()
        if not data:
            return None
        url = data.get("url")
        if not url:
            return None
        parsed = urlparse(url)
    
        # Check valid YouTube domains
        if parsed.hostname not in ('youtube.com', 'www.youtube.com', 'youtu.be'):
            raise ValueError("Invalid YouTube domain")

        video_id = None
        
        # Handle shortened youtu.be URLs
        if parsed.hostname == 'youtu.be':
            if parsed.path:
                video_id = parsed.path.split('/')[1] if parsed.path.count('/') >= 1 else None
        
        # Handle special paths (live, embed)
        elif parsed.path.startswith(('/live/', '/embed/')):
            path_parts = parsed.path.split('/')
            if len(path_parts) >= 3:
                video_id = path_parts[2]
        
        # Handle standard watch URLs
        elif parsed.path == '/watch':
            query = parse_qs(parsed.query)
            video_id = query.get('v', [None])[0]

        if not video_id or len(video_id) != 11:  # YouTube IDs are always 11 characters
            raise ValueError("Invalid YouTube video ID")
        
        return video_id.split('&')[0]  # Remove any extra parameters
    
    @staticmethod
    def youtube_url(video_id):
        return f"https://youtube.com/watch/v={video_id}"