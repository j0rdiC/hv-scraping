from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from factory import Browser, Scraper
import time


url = 'https://www.riu.com/es/hotel/espana/madrid/hotel-riu-plaza-espana/'


def test_reservation():
    browser = Browser()
    browser.get(url)

    # Accept cookies if present
    has_cookies = False
    try:
        print('Waiting for cookies...')
        accept_cookies_btn = browser.wait(type=By.ID, selector='onetrust-accept-btn-handler')
        accept_cookies_btn.click()
        has_cookies = True
    except TimeoutException:
        print('No cookies found')

    print('Has cookies: ', has_cookies)

    # Open calendar modal
    try:
        time.sleep(1)
        browser.find('divCalendario1', By.ID).click()
    except NoSuchElementException:
        print('Calendar entry not found')

    try:
        # time.sleep(1)
        calendars = browser.find_all('calendar-table', By.CLASS_NAME)
        print(f'{len(calendars)} calendar boxes found')

        # Get the td elements
        dates = calendars[1].find_elements(By.TAG_NAME, 'td')
        print(f'{len(dates)} dates found')
        dates_text = [date.text for date in dates]
        # Some strings may be empty, filter them out
        dates_text = list(filter(None, dates_text))
        print(len(dates_text))

        for date in dates:
            if date.text == '20':
                date.click()
                break  # necessary to avoid stale element exception

        dates = browser.find_all('calendar-table', By.CLASS_NAME)[1].find_elements(By.TAG_NAME, 'td')
        for date in dates:
            if date.text == '22':
                date.click()
                break

        # Submit dates
        browser.find('submitBuscador', By.ID).click()

    except NoSuchElementException:
        print('No element found')

    # Enter promo-code
    # promo_input_xpath = '//*[@id="inputPromoCode"]'
    # promo_input = browser.find(promo_input_xpath, By.XPATH)
    # promo_input.click()
    # promo_input.send_keys('RIU2021')


test_reservation()
