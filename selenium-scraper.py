#!/bin/env python3

import os
import sys
import json
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# firefox_options = Options()
# firefox_options.add_argument('--headless')
driver: WebDriver = webdriver.Firefox()  # options=firefox_options)

test_urls = [
    'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=30%2F03%2F2023&hsri=02040&step=1',
    'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=12%2F04%2F2023&hsri=02040&step=1',
]


def err(info):
    print(f'Error: {info}')
    driver.quit()
    sys.exit(1)


def init(url):
    try:
        driver.get(url)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'h2')))

        # Scroll down the page a few times to trigger the loading of additional content
        for _ in range(5):
            driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.END)

        results = driver.find_element(By.CLASS_NAME, 'mi-rs-results')
        return results

    except Exception as e:
        err(e)


def extract_price(tarif):
    try:
        price = tarif.find_element(By.CLASS_NAME, 'mi-rs-rate-night-price').text
        return int(''.join(c for c in price if c.isdigit()))

    except Exception as e:
        err(e)


def extract_rooms(results):
    try:
        rooms = []
        room_cards = results.find_elements(By.CLASS_NAME, 'mi-rs-room-header')
        room_names = [room.find_element(By.TAG_NAME, 'h2') for room in room_cards]

        for room in room_names:
            rooms.append({'name': room.text})

        tarifs = []
        tarif_cards = results.find_elements(By.CLASS_NAME, 'mi-rs-rate')

        for t in tarif_cards:
            tarif = {}
            name = t.find_element(By.TAG_NAME, 'h3').text
            tarif[name] = {}  # { regime: price }

            radio_containers = t.find_elements(By.CLASS_NAME, 'mi-radio-container')

            if not radio_containers:
                regime = t.find_element(By.TAG_NAME, 'p').text
                tarif[name][regime] = extract_price(t)
            else:
                for radio in radio_containers:
                    regime = radio.text
                    radio_button = radio.find_element(By.CLASS_NAME, 'mi-radio-ico')
                    radio_button.click()

                    tarif[name][regime] = extract_price(t)

            tarifs.append(tarif)
        return rooms, tarifs

    except Exception as e:
        err(e)


def output(data, test_num):
    rooms, tarifs = data

    hotel = {
        'name': 'Las Gaviotas',
        'currency': 'EUR',
        'rooms': [],
    }

    try:
        for i, room in enumerate(rooms):
            room['tarifs'] = tarifs[i:i+2]
            hotel['rooms'].append(room)

        current_path = Path(__file__).parent
        if not os.path.exists(current_path / 'output'):
            os.mkdir(current_path / 'output')

        file_name = f'{current_path}/output/las-gaviotas-{test_num}.json'
        with open(file_name, 'w') as f:
            json.dump(hotel, f, indent=2)

    except Exception as e:
        err(e)


### TEST ###
def make_reservation():
    """Choose entry and exit dates"""
    try:
        driver.get('https://www.hotellasgaviotas.com/')
        checkin = driver.find_element(By.ID, 'checkin')
        checkin.click()
        checkin.send_keys('30/03/2023')

        checkout = driver.find_element(By.ID, 'checkout')
        checkout.click()
        checkout.send_keys('31/03/2023')

        # Click on the search button
        search = driver.find_element(By.ID, 'search')
        search.click()

    except Exception as e:
        err(e)


def main():
    for i, url in enumerate(test_urls):
        results = init(url)
        data = extract_rooms(results)
        output(data, i)
        driver.delete_all_cookies()

    driver.quit()


if __name__ == '__main__':
    main()
