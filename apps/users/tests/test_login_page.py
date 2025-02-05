import pytest
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from apps.users.models import CustomUser
from selenium import webdriver

@pytest.mark.selenium
def test_login_with_email_only(live_server, chrome_browser_instance: webdriver.Chrome):
    browser = chrome_browser_instance
    browser.get(live_server.url + '/accounts/login/')
    assert "Login" in browser.title
