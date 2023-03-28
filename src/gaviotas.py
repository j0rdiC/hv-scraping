#!/bin/env python3

import os
import sys
import json
import re
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys

from .browser import Browser


# firefox_options = Options()
# firefox_options.add_argument('--headless')

test_urls = [
    'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=30%2F03%2F2023&hsri=02040&step=1',
    'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=12%2F04%2F2023&hsri=02040&step=1',
]


def err(info):
    print(f'Error: {info}')
    browser.quit()
    sys.exit(1)


def init(url):
    try:
        global browser
        browser = Browser()
        browser.get(url)
        browser.wait(selector='h2')
        browser.scroll(5)
        results = browser.find('mi-rs-results', By.CLASS_NAME)

        return results

    except Exception as e:
        err(e)


def extract_price(tarif):
    try:
        price = tarif.find_element(By.CLASS_NAME, 'mi-rs-rate-night-price').text
        return int(''.join(c for c in price if c.isdigit()))

    except Exception as e:
        err(e)


def extract_data(results):
    """Extract data from the results page"""

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


def output(data, test_num, hotel_name):
    """Save data to a JSON file"""

    rooms, tarifs = data
    currency = re.search(r'currency=(\w+)', browser.driver.current_url)
    currency = currency.group(1) if currency else 'EUR'

    hotel = {
        'name': 'Las Gaviotas',
        'currency': currency,
        'rooms': [],
    }

    try:
        for i, room in enumerate(rooms):
            room['tarifs'] = tarifs[i:i+2]
            hotel['rooms'].append(room)

        current_path = Path(__file__).parent.parent.resolve()
        if not os.path.exists(current_path / 'output'):
            os.mkdir(current_path / 'output')

        if not os.path.exists(current_path / 'output' / hotel_name):
            os.mkdir(current_path / 'output' / hotel_name)

        file_name = f'{hotel_name}_{test_num}.json'
        file_path = os.path.join(current_path, 'output', hotel_name, file_name)

        with open(file_path, 'w') as f:
            json.dump(hotel, f, indent=2)

    except Exception as e:
        err(e)


### TEST ###
# def make_reservation(from_date, to_date):
#     """Choose entry and exit dates"""
#     try:
#         browser.get('https://www.hotellasgaviotas.com/')
#         # can i find an element by its tag and class name?
#         open_chekin_modal = browser.find(By.CLASS_NAME, 'home-slideshow__action.js-book-toggle')
#
#         checkin = browser.find_element(By.ID, 'checkin')
#         checkin.click()
#         checkin.send_keys('30/03/2023')
#
#         checkout = browser.find_element(By.ID, 'checkout')
#         checkout.click()
#         checkout.send_keys('31/03/2023')
#
#         # Click on the search button
#         search = browser.find_element(By.ID, 'search')
#         search.click()
#
#     except Exception as e:
#         err(e)


def main():
    for i, url in enumerate(test_urls):
        results = init(url)
        data = extract_data(results)
        output(data, i, 'lasgaviotas')
        browser.driver.delete_all_cookies()

    browser.quit()
