import yt_dlp

def get_formats(url):
    try:
        ydl_opts = {
            "quiet": True,
            "skip_download": True,
        }
        formats_list = []
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for fmt in info.get("formats", []):
                if fmt.get("filesize") and fmt.get("ext") in ["mp4", "m4a"]:
                    formats_list.append({
                        "format_id": fmt["format_id"],
                        "ext": fmt["ext"],
                        "quality": fmt.get("format_note") or fmt.get("height"),
                        "filesize": f"{round(fmt['filesize'] / 1024 / 1024, 2)} MB",
                        "type": "video" if "video" in fmt.get("format", "") else "audio",
                    })
        return formats_list
    except Exception as e:
        print(f"❌ Error in get_formats: {e}")
        return []

def download_audio(url, format_id="bestaudio"):
    ydl_opts = {
        "format": format_id,
        "outtmpl": "downloaded_audio.%(ext)s",
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "192",
        }],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info).replace(".webm", ".mp3")

def download_video(url, format_id="best"):
    ydl_opts = {
        "format": format_id,
        "outtmpl": "downloaded_video.%(ext)s",
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url)
        return ydl.prepare_filename(info)
