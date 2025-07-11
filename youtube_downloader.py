from yt_dlp import YoutubeDL
import os
import imageio_ffmpeg

# Locate ffmpeg and make sure it's added to the system PATH
ffmpeg_path = imageio_ffmpeg.get_ffmpeg_exe()
os.environ["PATH"] += os.pathsep + os.path.dirname(ffmpeg_path)


def get_formats(url):
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False,
    }

    formats_list = []
    preferred_resolutions = ["360", "480", "720", "1080"]

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)

            for f in info['formats']:
                if f.get("vcodec") != "none":
                    height = f.get("height")
                    ext = f.get("ext")
                    if height and str(height) in preferred_resolutions and ext == "mp4":
                        size = f.get("filesize") or 0
                        formats_list.append({
                            "format_id": f["format_id"],
                            "ext": ext,
                            "resolution": f"{height}p",
                            "filesize": size
                        })

        return formats_list

    except Exception as e:
        print("❌ Error in get_formats:", str(e))
        return []


def download_audio(url, output_name="audio"):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{output_name}.%(ext)s',
        'quiet': True,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info).replace(".webm", ".mp3").replace(".m4a", ".mp3")
            return filename
    except Exception as e:
        print("❌ Error in download_audio:", str(e))
        return None


def download_video(url, format_id, output_name="video"):
    ydl_opts = {
        'format': format_id + '+bestaudio/best',
        'outtmpl': f'{output_name}.%(ext)s',
        'quiet': True,
        'merge_output_format': 'mp4',
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            return filename
    except Exception as e:
        print("❌ Error in download_video:", str(e))
        return None
