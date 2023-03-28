import os
import sys
import json
from pathlib import Path

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup

from .browser import Browser


test_urls = [
    'https://www.riu.com/es/booking/rooms?search=%7B%22tipoBusqueda%22:%22TIPO_BUSQUEDA_HOTEL%22,%22paisDestino.pais%22:%22Espa%C3%B1a%22,%22paisDestino.id_pais%22:%22Espa%C3%B1a%22,%22paisDestino.destino%22:%22z_201058%22,%22paisDestino.destino_name%22:%22Madrid%22,%22paisDestino.id_destino%22:%22Madrid%22,%22paisDestino.hotel_name%22:%22Hotel%20Riu%20Plaza%20Espa%C3%B1a%22,%22paisDestino.hotel%22:%22582%22,%22huespedes.numeroHabitaciones%22:1,%22huespedes.habitaciones%5B0%5D.numeroAdultos%22:2,%22huespedes.habitaciones%5B0%5D.numeroNinos%22:0,%22numeroAdultosTotal%22:2,%22numeroNinosTotal%22:0,%22fechas.fechaEntradaAsString%22:%2210%2F04%2F2023%22,%22fechas.fechaSalidaAsString%22:%2211%2F04%2F2023%22,%22dateFormat.formato%22:%22DD%2FMM%2FYYYY%22,%22fechaEntradaMs%22:1681077600000,%22fechaSalidaMs%22:1681164000000,%22codigoPromocional%22:%22%22%7D',
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
        print('Waiting for page to load...')
        browser.wait(selector='h3')
        browser.scroll(5)
        print('Loading results...')
        results = browser.find('riu-hotels-list', By.CLASS_NAME)

        return results

    except Exception as e:
        err(e)


def extract_data(results):
    """Extract data from the results page"""

    try:
        print('Extracting data...')
        soup = BeautifulSoup(results.get_attribute('innerHTML'), 'html.parser')
        room_containers = soup.find_all('div', class_='room')

        rooms = []
        for room in room_containers:
            name = room.find('span', class_='descripcion').string
            regime = room.find('div', class_='room__footer-board-text').find('span').string
            price_container = room.find('div', class_='room-footer__price-final')
            price = price_container.find('strong').string
            currency = price_container.find('sub').string

            rooms.append({
                'name': name,
                'regime': regime,
                'price': float(price.replace(',', '.')),
                'currency': currency.strip()
            })

            # or { 'name': name, regime: price }

        print('Data extracted successfully!')
        return rooms

    except Exception as e:
        err(e)


def output(data, test_num, hotel_name):
    """Save data to a JSON file"""

    hotel_data = {
        'name': hotel_name,
        'results': len(data),
        'rooms': data
    }

    try:
        print('Saving data to JSON file...')
        current_path = Path(__file__).parent.parent.resolve()
        if not os.path.exists(current_path / 'output'):
            os.mkdir(current_path / 'output')
        if not os.path.exists(current_path / 'output' / hotel_name):
            os.mkdir(current_path / 'output' / hotel_name)

        file_name = f'{hotel_name}_{test_num}.json'
        file_path = os.path.join(current_path, 'output', hotel_name, file_name)

        with open(file_path, 'w') as f:
            json.dump(hotel_data, f, indent=2)

        print(f'{file_name} saved successfully!')

    except Exception as e:
        err(e)


def main(hotel_name):
    for i, url in enumerate(test_urls):
        results = init(url)
        data = extract_data(results)
        output(data, i, hotel_name)
        browser.driver.delete_all_cookies()

    browser.quit()
