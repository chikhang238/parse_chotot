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

TIMEOUT = 30
BASE_URL = "https://chotot.com"
CHOTOT = "chotot"
HTM = "htm"


class CrawlHTML(object):
    """
    Crawl HTML of given links and also crawl all 
    possible links which are not in given list
    @param queue is the provided list which is sent to queue
    @param result is list of all post links
    @param post_count is the number of post urls
    @param nonpost_count is the number of crawled non-post urls
    """

    def __init__(self, given_list):
        self.driver = None
        self.queue = given_list
        self.result = []
        self.html = []
        self.post_count = 0
        self.nonpost_count = 0

    def check_if_url_is_post(self, url):
        #print("consider:", url)
        if HTM in url and self.check_url(url):
            if url not in self.result:
                pagesrc = self.get_html(url)
                if pagesrc is not None:   
                    self.result.append(url)
                    self.html.append(pagesrc)
                    self.post_count = self.post_count + 1
                    print("Post link number:", self.post_count)
        else:
            if url not in self.queue:
                #print("Non-post link:", url)
                self.queue.append(url)
                self.nonpost_count = self.nonpost_count + 1
                print("Non-post link number:", self.nonpost_count)
        #print("")

    def check_url(self, url):
        """
        Check whether an url is valid or not
        """
        return True

    def set_connection(self, url):
        """
        Return Beautifulsoup object
        """
        try:
            self.driver.get(url)
            self.driver.set_page_load_timeout(TIMEOUT)
            html = self.driver.page_source 
            soup = BeautifulSoup(html, 'html.parser')
            return soup
        except:
            print('Connot access this link !!!')
            return None

    def get_html(self, url):
        """
        Get HTML (page source) of a given url
        """
        try:
            self.driver.get(url)
            self.driver.set_page_load_timeout(TIMEOUT)
            return self.driver.page_source
        except:
            print('Connot access this post-url !!!')
            return None

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
        self.driver = webdriver.Firefox(executable_path='/home/chikhang/Downloads/geckodriver', options=options)
        
        for url in self.queue:
            print('-'*10, 'STARTING TO CONSIDER THE URL', '-'*10)
            print(url)
            
            soup_object = self.set_connection(url)
            if soup_object is None:
                continue

            relative_urls = soup_object.find_all('a', {'href': re.compile('^/')})
            absolute_urls = soup_object.find_all('a', {'href': re.compile('^https://www.chotot')})
            
            considered_list = []
            for element in relative_urls:
                abs_ele = BASE_URL + element['href']
                considered_list.append(abs_ele)
            for element in absolute_urls:
                if CHOTOT in element['href']:
                    considered_list.append(element['href'])

            print("Number of links which are retreived from url:", len(considered_list))
            #a = 0
            temp_list = considered_list.copy()
            for child_url in temp_list:
                self.check_if_url_is_post(child_url)
                considered_list.remove(child_url)
                #a += 1
            #print(a)
            print("-- NUMBER OF CRAWLED POST URLS =", self.post_count)

            print('-'*10, 'FINISHING TO CONSIDER THE URL', '-'*10)
            print("")

            if self.post_count >= 100:
                break
        
        print('CRAWLING DONE')

    def save_tocsv(self):
        dic = {"Links": self.result, "HTML": self.html}
        data = pd.DataFrame(dic)
        data.to_csv('post_urls_1.csv')
        print('TASK DONE')
            
