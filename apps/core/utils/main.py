import datetime
import cv2
from ..models import *
def get_duration(filename):
    video = cv2.VideoCapture(filename)
    fps = int(video.get(cv2.CAP_PROP_FPS))
    frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
    # print(frame_count)
    seconds = frame_count // fps
    video_time = datetime.timedelta(seconds=seconds)
    return video_time

def create_certificate(course, student):
    inst = Certificate.objects.create(course=course, student=student) 
    return inst

def create_certificate_pdf(fullname, instructor_name, key, course_name):
    pass
