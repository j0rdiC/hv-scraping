from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import json
import os
from pathlib import Path


class Browser:
    def __init__(self):
        self.driver = webdriver.Firefox()

    def get(self, url):
        self.driver.get(url)

    def wait(self, time=10, type=By.TAG_NAME, selector='h2'):
        return WebDriverWait(self.driver, time).until(
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

    # def __del__(self):
    #     self.quit()


class Scraper(Browser):
    def __init__(self, url: str, selector: str, type=By.TAG_NAME, scroll: int = 5):
        super().__init__()
        self.url = url
        self.get(self.url)
        print('Waiting for page to load...')
        self.wait(type=type, selector=selector)
        self.scroll(scroll)

    def fetch_html(self, selector, type):
        print(f'Fetching {selector}...')
        return self.driver.find_element(type, selector)

    def parse_html(self, html):
        print('Parsing HTML...')
        return BeautifulSoup(html.get_attribute('innerHTML'), 'html.parser')

    def get_parsed_results(self, selector, type=By.CLASS_NAME):
        html = self.fetch_html(selector, type)
        return self.parse_html(html)

    def json_output(self, data, name, test_num):
        try:
            print('Saving data to JSON file...')
            output_path = Path(__file__).parent.parent.resolve()
            if not os.path.exists(output_path / 'output'):
                os.mkdir(output_path / 'output')
            if not os.path.exists(output_path / 'output' / name):
                os.mkdir(output_path / 'output' / name)

            file_name = f'{name}_{test_num}.json'
            file_path = os.path.join(output_path, 'output', name, file_name)

            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            print(f'{file_name} saved successfully!')
        except Exception as e:
            print(f'Error saving file: {e}')
