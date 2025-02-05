import os
import subprocess
import logging
from celery import shared_task
from django.conf import settings
from django.apps import apps
from django.core.cache import cache
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=2)
def convert_to_hls(self, video_id):
    Video = apps.get_model("core", "Video")
    
    try:
        video = Video.objects.get(id=video_id)
        input_path = video.video.path
        output_dir = os.path.join(settings.MEDIA_ROOT, "hls", str(video.id))
        os.makedirs(output_dir, exist_ok=True)

        quality_levels = [
            {"resolution": "1280x720", "bitrate": "2500k", "name": "720p"},
            {"resolution": "854x480", "bitrate": "1500k", "name": "480p"},
            {"resolution": "640x360", "bitrate": "800k", "name": "360p"},
        ]

        # Create stream directories
        for level in quality_levels:
            os.makedirs(
                os.path.join(output_dir, f"stream_{level['name']}"), exist_ok=True
            )

        # Master playlist preparation
        master_playlist_path = os.path.join(output_dir, "master.m3u8")

        # HLS conversion for each quality level
        for level in quality_levels:
            ffmpeg_command = [
                "ffmpeg",
                "-i",
                input_path,
                "-filter:v",
                f"scale={level['resolution']}",
                "-c:a",
                "aac",
                "-b:v",
                level["bitrate"],
                "-maxrate",
                level["bitrate"],
                "-bufsize",
                f"{level['bitrate']}",
                "-b:a",
                "128k",
                "-hls_time",
                "4",
                "-hls_list_size",
                "0",
                "-hls_segment_filename",
                os.path.join(output_dir, f"stream_{level['name']}/segment_%03d.ts"),
                os.path.join(output_dir, f"stream_{level['name']}/playlist.m3u8"),
            ]

            try:
                subprocess.run(
                    ffmpeg_command,
                    check=True,
                    capture_output=True,
                    text=True,
                )
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                logger.error(f"FFmpeg conversion failed for {level['name']}: {e}")
                raise

        # Create master playlist
        with open(master_playlist_path, "w") as master_playlist:
            master_playlist.write("#EXTM3U\n")
            for level in quality_levels:
                master_playlist.write(
                    f'#EXT-X-STREAM-INF:BANDWIDTH={int(level["bitrate"].rstrip("k"))*1000},'
                    f'RESOLUTION={level["resolution"]}\n'
                    f'stream_{level["name"]}/playlist.m3u8\n'
                )

        # Update video model
        video.master_playlist = os.path.join("hls", str(video.id), "master.m3u8")
        video.status = "ready"

        logger.info(f"HLS conversion completed for video {video_id}")

    except Video.DoesNotExist:
        video.status = "failed"
        logger.error(f"Video with ID {video_id} not found")
        raise
    except Exception as exc:
        video.status = "failed"
        logger.error(f"Unexpected error in HLS conversion: {exc}")
        raise self.retry(exc=exc)
    video.save()


@shared_task
def video_progress_synchronizer():
    UserCourseProgress = apps.get_model("core", "UserCourseProgress")
    """
    video_progress {
        user_id: {
            video_id: {
                watched_to: 0.5
            }
        }
    }
    """
    data = cache.get("video_progress")

    data = cache.get("video_progress")
    if data is None:
        print("No data found in cache. Initializing empty cache.")
        cache.set("video_progress", {})
        return

    data_processed = {}
    for user_id, videos in data.items():
        for video_id, video_data in videos.items():
            try:
                UserCourseProgress.objects.filter(
                    student__id=user_id, video__id=video_id
                ).update(progress=video_data["watched_to"])

                data_processed[(user_id, video_id)] = True
            except Exception as e:
                pass

    for user_id, videos in list(data.items()): 
        for video_id in list(videos.keys()):  
            if data_processed.get((user_id, video_id)):
                del data[user_id][video_id]

        # Remove empty user entries from the cache
        if not data[user_id]:
            del data[user_id]

    # Update the cache with the cleaned data
    cache.set("video_progress", data)
