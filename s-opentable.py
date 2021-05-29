from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from datetime import datetime, date, timedelta
from random import randint
import time
import configparser

# read config file
config = configparser.ConfigParser()
config.read('config.ini')
early = config['general']['early']
late = config['general']['late']
restaurants = config['general']['open_restaurants'].split(',')

# successful availabilities placeholder
success = []

# set up the Selenium browser
browser = webdriver.Chrome('./chromedriver')

# date calculation for full range of dates
today = date.today()
friday = today + timedelta((4-today.weekday())%7)
dates = [friday]
additional_dates = [1,7,8,14,15,21,22]
for day in additional_dates:
    dates.append(friday+timedelta(days=day))

for restaurant in restaurants:

    # define the URL 
    url = F'https://www.opentable.com/r/{restaurant}'
    print(url)

    # loop through dates
    for day in dates:
        formatted_day = day.strftime("%a, %b %#d, %Y")

        # load the OpenTable page and get select a date
        browser.get(url)
        date_selector = browser.find_element_by_xpath("//button[@class='ddb7cc3c _89c5e25a _74cd82ef']")
        date_selector.click()
        select_date = browser.find_element_by_xpath(F"//div[@aria-label='{formatted_day}']")
        select_date.click()
        find_table_button = browser.find_element_by_xpath("//button[@class='aae89208 _7a37c88f _46ec4deb']")
        find_table_button.click()
        time.sleep(randint(1,3))

        # loop through and capture dates
        avail_times = browser.find_elements_by_xpath(F"//div[@data-auto='timeslot']")
        for avail in avail_times:
            avail_time = avail.find_element_by_xpath(".//span").text
            if datetime.strptime(early,'%H:%M%p') <= datetime.strptime(avail_time,'%H:%M %p') < datetime.strptime(late,'%H:%M%p'):
                success.append((restaurant, formatted_day, avail_time, url))

print(success)

# close the browser session
browser.close()