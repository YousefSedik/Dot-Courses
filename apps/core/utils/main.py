import datetime
import cv2

def get_duration(filename):
    video = cv2.VideoCapture(filename)
    fps = video.get(cv2.CAP_PROP_FPS)
    frame_count = video.get(cv2.CAP_PROP_FRAME_COUNT)
    seconds = frame_count // fps
    video_time = datetime.timedelta(seconds=seconds)
    return video_time