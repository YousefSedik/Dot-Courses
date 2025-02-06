# from django.core.management.base import BaseCommand
# from django.contrib.auth.models import Group
# from django.contrib.auth.models import Permission

# class Command(BaseCommand):
#     help = "Create an instructor group"

#     def handle(self, *args, **kwargs):
#         # create the group
#         group, created = Group.objects.get_or_create(name='instructor')
#         # get the permissions
#         permissions = Permission.objects.filter(codename__contains='instructor')
#         print(permissions)

