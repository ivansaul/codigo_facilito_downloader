"""
Video download model
"""

from ..errors import DownloadError


class YoutubeDLLogger:
    """Custom yt-dlp logger"""

    def debug(self, msg):
        """Debug message"""
        print(msg)

    def info(self, msg):
        """Info message"""
        print(msg)

    def warning(self, msg):
        """Warning message"""
        print(msg)

    def error(self, msg):
        """Error message"""
        raise DownloadError(f"Downloading video failed. {msg}")

    # TODO: implement custom parser for progress bar 👇
    @staticmethod
    def on_progress(d):
        """Progress callback"""
        if d["status"] == "finished":
            print("Done downloading")
        elif d["status"] == "downloading":
            print(f"Downloading... progress: {d['_percent_str']}")
        elif d["status"] == "error":
            print(f"Error during download: {d['error']}")
