from apps.core import models

def run():
    # create rate obj 
    db_course = models.Course.objects.filter(name='Database').first()
    student  = models.get_user_model().objects.filter(email="maxxd1919@gmail.com").first()
    inst = models.Rate.objects.all().first()
    inst.rate='1'
    inst.save()
