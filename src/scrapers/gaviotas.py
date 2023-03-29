import os
import sys
import json
import re
from pathlib import Path
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from ..factory import Scraper


# firefox_options = Options()
# firefox_options.add_argument('--headless')

test_urls = [
    # 'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=30%2F03%2F2023&hsri=02040&step=1',
    'https://www.hotellasgaviotas.com/bookingstep1.es.html?idtokenprovider=100376436&nights=1&clientCodeStrictSearch=true&parties=W3siYWR1bHRzIjoyLCJjaGlsZHJlbiI6W119XQ%3D%3D&lang=es&home=http%3A%2F%2Fwww.hotellasgaviotas.com%2F&currency=EUR&applyClubDiscount=true&deviceType=DESKTOP_TABLET&checkin=12%2F04%2F2023&hsri=02040&step=1',
]


def err(info):
    print(f'Error: {info}')
    scraper.quit()
    sys.exit(1)


def init(url):
    global scraper
    scraper = Scraper(url, selector='h2')
    print('Loading results...')
    results = scraper.fetch_html('mi-rs-results', By.CLASS_NAME)

    return results if results else err('No results found')


def extract_price(tarif):
    try:
        price = tarif.find_element(By.CLASS_NAME, 'mi-rs-rate-night-price').text
        return int(''.join(c for c in price if c.isdigit()))
    except Exception as e:
        print('Error extracting price:', e)


def extract_data(results):
    print('Extracting data...')
    room_containers = results.find_elements(By.CLASS_NAME, 'mi-rs-room')
    rooms = []
    for room in room_containers:
        room_name = room.find_element(By.TAG_NAME, 'h2').text
        tarif_containers = room.find_elements(By.CLASS_NAME, 'mi-rs-rate')
        tarifs = []
        for t in tarif_containers:
            tarif = {}
            tarif_name = t.find_element(By.TAG_NAME, 'h3').text
            tarif[tarif_name] = {}  # { regime: price }

            # Only one price is displayed at a time if there are multiple regimes
            radio_containers = t.find_elements(By.CLASS_NAME, 'mi-radio-container')
            if not radio_containers:
                regime = t.find_element(By.TAG_NAME, 'p').text
                tarif[tarif_name][regime] = extract_price(t)
            else:
                for radio in radio_containers:
                    regime = radio.text
                    radio_button = radio.find_element(By.CLASS_NAME, 'mi-radio-ico')
                    radio_button.click()
                    tarif[tarif_name][regime] = extract_price(t)

            tarifs.append(tarif)

        rooms.append({
            'name': room_name,
            'tarifs': tarifs,
        })

    currency = re.search(r'currency=(\w+)', scraper.driver.current_url)
    currency = currency.group(1) if currency else '?EUR'

    # '&checkin=12%2F04%2F2023&'
    checkin = re.search(r'checkin=(.+?)&', scraper.driver.current_url)
    checkin = checkin.group(1) if checkin else '?'

    checkin_date = '/'.join(checkin.split('%2F'))
    checkin_date = datetime.strptime(checkin_date, '%d/%m/%Y').strftime('%d/%m/%Y')

    nights = re.search(r'nights=(\d+)', scraper.driver.current_url)
    nights = int(nights.group(1)) if nights else '?'

    checkout_date = datetime.strptime(checkin_date, '%d/%m/%Y') + timedelta(days=int(nights))
    checkout_date = checkout_date.strftime('%d/%m/%Y')

    return rooms, currency, checkin_date, checkout_date, nights


def format_data(data, hotel_name):
    rooms, currency, checkin_date, checkout_date, nights = data
    formated_data = {
        'name': hotel_name,
        'results': len(rooms),
        'currency': currency,
        'checkin': checkin_date,
        'checkout': checkout_date,
        'nights': nights,
        'rooms': rooms,
    }

    return formated_data


def main(hotel_name):
    for i, url in enumerate(test_urls):
        results = init(url)
        data = extract_data(results)
        formated_data = format_data(data, hotel_name)
        scraper.json_output(formated_data, hotel_name, i)
