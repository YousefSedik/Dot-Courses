from apps.core import models
import cv2
from apps.core.utils import main
import datetime
def run():
    # make the durations 0 for all courses 
    for course in models.Course.objects.all():
        course.duration = datetime.timedelta()
        
        videos = course.video_set.all() 
        for video in videos:
            course.duration += main.get_dur(video.video.path)
    
        course.save()
