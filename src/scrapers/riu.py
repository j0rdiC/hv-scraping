import os
import sys
import json
from pathlib import Path
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from ..factory import Scraper, BeautifulSoup


test_urls = [
    'https://www.riu.com/es/booking/rooms?search=%7B%22tipoBusqueda%22:%22TIPO_BUSQUEDA_HOTEL%22,%22paisDestino.pais%22:%22Espa%C3%B1a%22,%22paisDestino.id_pais%22:%22Espa%C3%B1a%22,%22paisDestino.destino%22:%22z_201058%22,%22paisDestino.destino_name%22:%22Madrid%22,%22paisDestino.id_destino%22:%22Madrid%22,%22paisDestino.hotel_name%22:%22Hotel%20Riu%20Plaza%20Espa%C3%B1a%22,%22paisDestino.hotel%22:%22582%22,%22huespedes.numeroHabitaciones%22:1,%22huespedes.habitaciones%5B0%5D.numeroAdultos%22:2,%22huespedes.habitaciones%5B0%5D.numeroNinos%22:0,%22numeroAdultosTotal%22:2,%22numeroNinosTotal%22:0,%22fechas.fechaEntradaAsString%22:%2210%2F04%2F2023%22,%22fechas.fechaSalidaAsString%22:%2211%2F04%2F2023%22,%22dateFormat.formato%22:%22DD%2FMM%2FYYYY%22,%22fechaEntradaMs%22:1681077600000,%22fechaSalidaMs%22:1681164000000,%22codigoPromocional%22:%22%22%7D',
]


def err(info):
    print(f'Error: {info}')
    scraper.quit()
    sys.exit(1)


def init(url):
    global scraper
    scraper = Scraper(url, selector='h3', scroll=5)
    print('Loading results...')
    results = scraper.get_parsed_results('riu-hotels-list')

    return results


def extract_data(results: BeautifulSoup):
    print('Extracting data...')
    room_containers = results.find_all('div', class_='room')

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

    # 'fechas.fechaEntradaAsString%22:%2210%2F04%2F2023%22,%22fechas.fechaSalidaAsString%22:%2211%2F04%2F2023%22,'
    current_url = scraper.driver.current_url
    checkin = current_url.split('fechaEntradaAsString%22:%22')[1].split('%22')[0]
    checkout = current_url.split('fechaSalidaAsString%22:%22')[1].split('%22')[0]
    checkin_date = '/'.join(checkin.split('%2F'))
    checkout_date = '/'.join(checkout.split('%2F'))

    nights = (datetime.strptime(checkout_date, '%d/%m/%Y') - datetime.strptime(checkin_date, '%d/%m/%Y')).days
    for room in rooms:
        room['price_per_night'] = room['price'] / nights

    print('Data extracted successfully!')
    return rooms, checkin_date, checkout_date


def format_data(data, hotel_name):
    rooms, checkin_date, checkout_date = data
    formatted_data = {
        'name': hotel_name,
        'results': len(rooms),
        'checkin_date': checkin_date,
        'checkout_date': checkout_date,
        'rooms': rooms,

    }

    return formatted_data


def main(hotel_name):
    for i, url in enumerate(test_urls):
        results = init(url)
        data = extract_data(results)
        formated_data = format_data(data, hotel_name)
        scraper.json_output(formated_data, hotel_name, i)


def gen_url(checkin, checkout):
    # '%22fechas.fechaEntradaAsString%22:%2210%2F04%2F2023%22,%22fechas.fechaSalidaAsString%22:%2211%2F04%2F2023%22,%22dateFormat.formato%22:%22DD%2FMM%2FYYYY%22,%22fechaEntradaMs%22:1681077600000,%22fechaSalidaMs%22:1681164000000'
    chekin_ms = int(datetime.strptime(checkin, '%d/%m/%Y').timestamp() * 1000)
    checkout_ms = int(datetime.strptime(checkout, '%d/%m/%Y').timestamp() * 1000)

    checkin_url = '%2F'.join(checkin.split('/'))
    checkout_url = '%2F'.join(checkout.split('/'))

    url = f"""https://www.riu.com/es/booking/rooms?search=%7B%22tipoBusqueda%22:%22TIPO_BUSQUEDA_HOTEL%22,%22paisDestino.pais%22:%22Espa%C3%B1a%22,%22paisDestino.id_pais%22:%22Espa%C3%B1a%22,%22paisDestino.destino%22:%22z_201058%22,%22paisDestino.destino_name%22:%22Madrid%22,%22paisDestino.id_destino%22:%22Madrid%22,%22paisDestino.hotel_name%22:%22Hotel%20Riu%20Plaza%20Espa%C3%B1a%22,%22paisDestino.hotel%22:%22582%22,%22huespedes.numeroHabitaciones%22:1,
    %22huespedes.habitaciones%5B0%5D.numeroAdultos%22:2,%22huespedes.habitaciones%5B0%5D.numeroNinos%22:0,
    %22numeroAdultosTotal%22:2,%22numeroNinosTotal%22:0,
    %22fechas.fechaEntradaAsString%22:%22{checkin_url}%22,
    %22fechas.fechaSalidaAsString%22:%22{checkout_url}%22,
    %22dateFormat.formato%22:%22DD%2FMM%2FYYYY%22,
    %22fechaEntradaMs%22:{chekin_ms},
    %22fechaSalidaMs%22:{checkout_ms},
    %22codigoPromocional%22:%22%22%7D"""
