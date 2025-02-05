import pytest
from django.contrib.auth import get_user_model

User = get_user_model()
@pytest.fixture(scope="function")
def create_admin_user(django_user_model):
    pass 