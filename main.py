import os
import pickle
import sys
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DRIVER_BIN = os.path.join(PROJECT_ROOT, "bin/chromedriver_v85_mac")

username = os.getenv("USERNAME")
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
interval = os.getenv("INTERVAL")

page_url = 'https://poshmark.ca'
login_url = page_url + '/login'
available_option = '?availability=available&condition=closet&all_size=true&my_size=false'
closet_url = page_url + '/closet/' + username + available_option
logout_url = page_url + '/logout'

driver = webdriver.Chrome(executable_path=DRIVER_BIN)
actions = ActionChains(driver)


def resolve_captcha():
    time.sleep(5)
    try:
        captcha_error_message = driver.find_element_by_xpath('//span[@data-error-type="DisplayCaptchaError"]')
        if captcha_error_message.text:
            print('Please login manually by completing the Captcha')

            password_input = driver.find_element_by_id("login_form_password")
            password_input.send_keys(password)

            i = 0
            while i != 100:
                time.sleep(i)
                print("Time: ", i)
                i += 1

            print('Script is now resuming')
    except NoSuchElementException:
        print("No captcha found")


def load_cookies():
    for cookie in pickle.load(open("PoshMarkCookies.pkl", "rb")):
        driver.add_cookie(cookie)


def input_login_info():
    username_input = driver.find_element_by_id("login_form_username_email")
    password_input = driver.find_element_by_id("login_form_password")

    username_input.send_keys(email)
    password_input.send_keys(password)


def login():
    driver.get(login_url)

    input_login_info()

    if os.path.exists("PoshMarkCookies.pkl"):
        load_cookies()

    login_button = driver.find_element_by_xpath('//button[@data-pa-name="login"]')
    login_button.click()

    resolve_captcha()

    if not os.path.exists("PoshMarkCookies.pkl"):
        pickle.dump(driver.get_cookies(), open("PoshMarkCookies.pkl", "wb"))


def load_all_listings():
    scroll_pause_time = 0.5

    driver.get(closet_url)

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(scroll_pause_time)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height


def share_to_followers(share_btn):
    actions.move_to_element(share_btn).perform()
    share_btn.click()

    time.sleep(1)
    to_my_followers = driver.find_element_by_class_name("share-wrapper-container")
    to_my_followers.click()

    time.sleep(5)


def share_listings(share_buttons):
    try:
        login_button = driver.find_element_by_class_name("header__login-signup")
        if login_button:
            print("Did not successfully login, please try again")
            sys.exit()
    except NoSuchElementException:
        print("Login successful")

    print("There are: ", len(share_buttons), " listings")

    i = 0
    for share_btn in share_buttons:
        share_to_followers(share_btn)
        i += 1
        print("Shared Listing: #", i)


def main():
    login()

    load_all_listings()

    share_buttons = driver.find_elements_by_xpath('//div[@data-et-name="share"]')
    while True:
        share_listings(share_buttons)
        time.sleep(int(interval))


if __name__ == '__main__':
    main()
