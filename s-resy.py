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
restaurants = config['general']['resy_restaurants'].split(',')

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

    # establish list for days with known no availability to avoid unnecessary page loads
    skip_days = [] 

    # loop through dates and pull time
    for day in dates:

        # if this date is known to have no availability, skip this loop interation
        if datetime(day.year, day.month, day.day) in skip_days:
            print(F'skipping: {day}')
            continue

        # define the URL 
        url = F'https://resy.com/cities/sf/{restaurant}?date={day}&seats=2'
        print(url)

        # load the Resy page and get save relevant reservation times
        browser.get(url)
        time.sleep(randint(3,6))
        times = browser.find_elements_by_class_name("time")
        type = browser.find_elements_by_class_name("type")
        for idx, avail in enumerate(times):
            if datetime.strptime(early,'%H:%M%p') <= datetime.strptime(avail.text,'%H:%M%p') < datetime.strptime(late,'%H:%M%p'):
                success.append((restaurant, day, avail.text, type[idx].text, url))

        # check future days to discount
        xpath = "//*[@id='page-content']/div[2]/div/article/section[1]/resy-inline-booking/div/div/resy-date-select-near/ng-container/div[11]/button"
        expand_view_button = browser.find_element_by_xpath(xpath)
        try:
            expand_view_button.click()
        except:
            print("No Button")
        sold_out = browser.find_elements_by_class_name("date.sold-out")
        for days in sold_out:
            message = days.get_attribute("aria-label")
            if message: 
                message = message[:len(message)-15]
                skip_date = datetime.strptime(message, "%A, %B %d")
                skip_date = datetime(2021, skip_date.month, skip_date.day)
                skip_days.append(skip_date)
                # print(skip_days)

print(success)

# close the browser session
browser.close()


