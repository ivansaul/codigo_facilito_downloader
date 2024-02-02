"""
Video download model
"""

import time

from ..errors import DownloadError


class YoutubeDLLogger:
    """Custom yt-dlp logger"""

    def debug(self, msg):
        """Debug message"""
        # print(msg)
        pass

    def info(self, msg):
        """Info message"""
        # print(msg)
        pass

    def warning(self, msg):
        """Warning message"""
        # print(msg)
        pass

    def error(self, msg):
        """Error message"""
        raise DownloadError(f"Downloading video failed. {msg}")

    # TODO: implement custom parser for progress bar 👇
    @staticmethod
    def wrapper_hook(file_name):
        def on_progress(d):
            """Progress callback"""
            if d["status"] == "finished":
                print("Done downloading")
                filename = d["filename"]
                print(file_name)
            elif d["status"] == "downloading":
                # print(f"\rDownloading... progress: {d['_percent_str']}", end="")
                print(
                    f"\rDownloading... {file_name}. {d['_default_template']} ",
                    end="",
                    flush=True,
                )
                time.sleep(0.1)
            elif d["status"] == "error":
                print(f"Error during download: {d['error']}")

        return on_progress
