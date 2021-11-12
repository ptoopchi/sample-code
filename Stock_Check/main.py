'''
For user privacy reasons some sections of code has been removed.
'''

import json
import time
import yaml
import requests
from bs4 import BeautifulSoup
from lxml import html
import re

from selenium import webdriver
from selenium.webdriver.common.by import By

# pip install webdriver-manager
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait 
from selenium.webdriver.support import expected_conditions as EC

import logging
import http.client as http_client

# pip install tk
from tkinter import Tk, Label, mainloop, Button

import smtplib
import pickle

import schedule
import datetime

# Method for getting website HTML text
def get_html_tree(link):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'}
    page = requests.get(link, headers=headers)
    return html.fromstring(page.content)

# Method to convert string to float
def extract_price(price_string):
    number = re.search('[0-9.]+', str(price_string)).group()
    return float(number)

# Method for checking price is compatible
def validate_price(price):
    if price < 550.0:
        return True
    return False

# Method for creating selenium instance
def get_chrome_driver(headless = False):
    options = webdriver.ChromeOptions()
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36'
    options.add_argument(f'user-agent={user_agent}')
    
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--user-data-dir=chrome-data") 

    if not headless:
        options.add_experimental_option("detach", True)
    else:
        options.add_argument('--headless')
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-gpu")
        options.add_argument("window-size=1280,960")
        options.add_argument('--disable-dev-shm-usage')
    
    return webdriver.Chrome(ChromeDriverManager().install(), options=options)

# Method for sending email to user
def send_email(user, pwd, recipients, subject, body):
    # Connect to gmail login
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(user, pwd)
        print('Successful login')
    except:
        print('Failed to login')

    # Send email to users
    FROM = user
    TO = recipients
    SUBJECT = subject
    TEXT = body

    message = """From: %s\nTo: %s\nSubject: %s\n\n%s
    """ % (FROM, ", ".join(TO), SUBJECT, TEXT)
    try:
        server.sendmail(FROM, TO, message)
        server.close()
        print('Successfully sent email')
    except:
        print('Failed to send email')

# Create simple popup with item in stock
def product_found_popup(product, company):
    root = Tk()
    root.title("Product Found!")
    root['background']='yellow'
    w = 800     
    h = 600     
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    x = (sw - w)/2
    y = (sh - h)/2
    root.geometry('%dx%d+%d+%d' % (w, h, x, y))
    m = "The " + product + " has been found on:"
    m += '\n'
    m += company
    w = Label(root, text=m, width=120, height=10, bg='yellow')
    w.config(font=("Courier", 20))
    w.pack()
    b = Button(root, text="Ok", command=root.destroy, width=5, bg='yellow')
    b.pack()
    mainloop()

# Notify user product is in stock
def notify(store):
    subject = 'FOUND PRODUCT!'
    product = "PRODUCT_NAME_HERE"
    recipients = ['EMAIL1@TESTING.com','EMAIL2@TESTING.com']

    body = product + ' has been found on ' + str(store['name']).capitalize()
    send_email('FAKE_EMAIL@EMAIL.com','FAKEPASSWORD', recipients, subject, body)
    product_found_popup(product, str(store['name']).capitalize())

# Read yaml file
def read_yaml_file():
    with open('config.yml') as f:
        return yaml.safe_load(f)['stores']
        
def store_run(store):
        # Loop through all links for store
        for link in store['link']:
            headless = store['headless']
            in_stock = False
            price = 0
            
            # Perform either headless or not headless data fetch
            if (headless == False):
                tree = get_html_tree(link)
            
                # Parameters for the tags
                price = tree.xpath(store['price'])

                price = extract_price(str(price))
                if tree.xpath(store['add_to_basket_button_id']):
                    in_stock = True
            else:
                # Connect to website 
                driver = get_chrome_driver(True)    
                driver.get(link)
                
                # Check if the item is in stock
                try:
                    price = extract_price(driver.find_element_by_xpath(store['price']).text)
                    if driver.find_element_by_xpath(store['add_to_basket_button_id']):
                        in_stock = True
                except:
                    in_stock = False
                # quit the main driver
                driver.quit()
            
            create_text_output_string = "\033[93m" + str(store['name']).capitalize() + "\033[0m Output Print: \n"

            # Checking print statements
            if (in_stock == True):
                create_text_output_string += "\033[92m Checking Price: " + str(price) + "\033[0m \n" + "\033[92m In stock: " + str(in_stock) + "\033[0m \n"
                print(create_text_output_string)
            else:
                create_text_output_string += "\033[1;31m Checking Price: " + str(price) + "\033[0m \n" + "\033[1;31m In stock: " + str(in_stock) + "\033[0m \n"
                print(create_text_output_string)
            
            # Add to basket and notify user
            if in_stock and validate_price(price):
                # Try again if the add to basket fails for some reason
                try:
                    notify(store)
                except:
                    time.sleep(0.5)
                    notify(store)
                

 # Main method for game
def main():
    # Fetch stores from yaml
    stores = read_yaml_file()
    
    for store in stores:
        store_run(store)

# Run Script
if __name__ == "__main__":
    # Run before schedule is executed
    main()
    # Run main() every 5 minutes
    schedule.every(5).minutes.do(main)
        
    while True:
        schedule.run_pending()
        time.sleep(1)






