import sys
import os
import json
import re
import requests
import pandas as pd
from time import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

TIMEOUT = 3
BASE_URL = "https://chotot.com"
CHOTOT = "chotot"
HTM = "htm"


class CrawlHTML(object):
    """
    Crawl HTML of given links and also crawl all 
    possible links which are not in given list
    @param queue is the provided list which is sent to queue
    @param result is list of all post links
    @param count is the number of post urls
    """

    def __init__(self, given_list):
        self.queue = given_list
        self.result = []
        self.count = 0

    def check_if_url_is_post(self, url):
        if HTM in url and check_url(url) and url not in self.result:
            self.result.append(url)
            self.count = self.count + 1
        else:
            self.queue.append(url)

    def check_url(self, url):
        """
        Check whether an url is valid or not
        """
        pass

    def set_connection(self, driver, url):
        """
        Return Beautifulsoup object
        """
        driver.get(url)

        try:
            driver.set_page_load_timeout(3)
        except:
            return None

        html = driver.page_source 
        soup = BeautifulSoup(html)
        return soup

    def main(self):
        """
        Set driver
        Step 1: Start with a queue of urls, retreive the first one
        Step 2: Check this url is valid or not
        Step 3: Set connection and retreive html of this url
        Step 4: Extract all urls from the content of the origin url
        Step 5: Check every urls which have already extracted,
        - Case 1: if this url is post url, check if it exist in result or not and add to this list
        - Case 2: It is not post url, check if it exists in queue or not, add to queue
        Step 6: Delete origin url and all checked urls
        Step 7: Check queue is empty or not come back to Step 1
        """
        options = Options()
        options.add_argument("--headless")
        driver = webdriver.Firefox(executable_path='/home/chikhang/Downloads/geckodriver', options=options)
        
        for url in self.queue:
            print('-'*10, 'STARTING TO CONSIDER THE URL', '-'*10)
            
            soup_object = self.set_connection(driver, url)
            if soup_object is None:
                continue

            relative_urls = soup_object.find_all('a', {'href': re.compile('^/')})
            absolute_urls = soup_object.find_all('a', {'href': re.compile('^https://')})
            
            considered_list = []
            for element in relative_urls:
                abs_ele = BASE_URL + element['href']
                considered_list.append(abs_ele)
            for element in absolute_urls:
                if CHOTOT in element:
                    considered_list.append(element)

            temp_list = considered_list
            for child_url in temp_list:
                self.check_if_url_is_post(child_url)
                considered_list.remove(child_url)

            print('-'*10, 'FININSHING TO CONSIDER THE URL', '-'*10)
        
        print('CRAWLING DONE')

    def save_tocsv(self):
        data = pd.DataFrame(self.result, columns = ['Links'])
        data.to_csv('post_urls.csv')
        print('TASK DONE')
            
