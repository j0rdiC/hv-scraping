from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from factory import Browser, Scraper
import time
from selenium.webdriver.common.action_chains import ActionChains


url = 'https://www.riu.com/es/hotel/espana/madrid/hotel-riu-plaza-espana/'
browser = Browser()


def accept_cookies():
    has_cookies = False
    try:
        print('Waiting for cookies...')
        accept_cookies_btn = browser.wait(type=By.ID, selector='onetrust-accept-btn-handler')
        accept_cookies_btn.click()
        has_cookies = True
        return has_cookies
    except TimeoutException:
        print('No cookies found')
        return has_cookies


def make_reservation():
    browser.get(url)

    # Accept cookies if present
    has_cookies = accept_cookies()
    print('Has cookies:', has_cookies)

    # Open calendar modal
    try:
        time.sleep(1)
        browser.find('divCalendario1', By.ID).click()
    except NoSuchElementException:
        print('Calendar entry not found')

    def extract_month(calendar):
        return calendar.find_element(By.CLASS_NAME, 'month').text

    def extract_days(calendar):
        return calendar.find_elements(By.TAG_NAME, 'td')

    def get_month(**kwargs):
        left, right = get_calendars()
        if kwargs.get('left'):
            return extract_month(left)
        elif kwargs.get('right'):
            return extract_month(right)

    def get_valid_days(days):
        valid_days = [day for day in days if 'off' not in day.get_attribute('class')]
        # return sorted(int(day) for day in set(filter(None, [day.text for day in valid_days])))
        return valid_days

    def get_days(**kwargs) -> list:
        left, right = get_calendars()
        if kwargs.get('left'):
            return get_valid_days(extract_days(left))
        elif kwargs.get('right'):
            return get_valid_days(extract_days(right))

    def get_calendars():
        calendar_left, calendar_right = browser.find_all('calendar-table', By.CLASS_NAME)
        return calendar_left, calendar_right

    try:
        month_left = get_month(left=True)
        month_right = get_month(right=True)

        days_left = get_days(left=True)
        days_right = get_days(right=True)
        entry_day = input(
            f'From {month_left} {days_left[0].text}-{days_left[-1].text} to {month_right} {days_right[0].text}-{days_right[-1].text}: ')

        m = entry_day.split()[0]
        d = entry_day.split()[1]

        if month_left.lower().startswith(m.lower()):
            for day in days_left:
                if day.text == d:
                    day.click()
                    break
        else:
            for day in days_right:
                if day.text == d:
                    day.click()
                    break

        days_left = get_days(left=True)
        days_right = get_days(right=True)
        # from entry day to ...
        exit_day = input(f'From {entry_day} to: ')

        m = exit_day.split()[0]
        d = exit_day.split()[1]

        if month_left.lower().startswith(m.lower()):
            for day in days_left:
                if day.text == d:
                    day.click()
                    break
        else:
            for day in days_right:
                if day.text == d:
                    day.click()
                    break

        # Submit dates
        time.sleep(1)
        browser.find('submitBuscador', By.ID).click()

    except NoSuchElementException:
        print('No element found')


def test_reservation():

    make_reservation()
    # browser.quit()
    ## FETCH DATA ##
    # time.sleep(5)
    # ## REPEAT RESERVATION ##
    # browser.driver.delete_all_cookies()
    # make_reservation()


test_reservation()
