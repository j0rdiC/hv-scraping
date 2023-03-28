import os
import sys
import json
import re
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Browser:
    def __init__(self):
        self.driver = webdriver.Firefox()

    def get(self, url):
        self.driver.get(url)

    def wait(self, time=10, type=By.TAG_NAME, selector='h2'):
        WebDriverWait(self.driver, time).until(
            EC.presence_of_element_located((type, selector))
        )

    # Scroll down the page N times to trigger the loading of additional content
    def scroll(self, times):
        for _ in range(times):
            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

    def find(self, selector, type):
        return self.driver.find_element(type, selector)

    def find_all(self, selector, type):
        return self.driver.find_elements(type, selector)

    def quit(self):
        self.driver.quit()

    def __del__(self):
        self.quit()
