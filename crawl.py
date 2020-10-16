import sys
import os
import json
import re
import hashlib
import validators
import pandas as pd
from time import time
from bs4 import BeautifulSoup
from selenium import webdriver
from datetime import datetime
from urllib.parse import urlsplit
from urllib.parse import urlparse
from elasticsearch import Elasticsearch
from selenium.webdriver.firefox.options import Options

TIMEOUT = 30
BASE_URL = "https://chotot.com"
CHOTOT = "chotot"
HTM = "htm"
NUM_URLS = 50


class CrawlHTML(object):
    """
    Crawl HTML of given links and also crawl all 
    possible links which are not in given list
    @param queue is the provided list which is sent to queue
    @param result is list of all post links
    @param post_count is the number of post urls
    @param nonpost_count is the number of crawled non-post urls
    @param es is the ElasticSearch object
    """

    def __init__(self, given_list):
        self.driver = None
        self.queue = given_list
        self.result = []
        self.html = []
        self.post_count = 0
        self.nonpost_count = 0
        self.es = Elasticsearch()

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

    def check_if_url_is_post(self, url):
        """
        Check whether an url is post url (the last level url) or not
        """
        #print("consider:", url)
        if HTM in url and self.check_url(url):
            if url not in self.result:
                pagesrc = self.get_html(url)
                if pagesrc is not None:   
                    self.result.append(url)
                    self.html.append(pagesrc)
                    self.save_to_elasticsearch(url, pagesrc)
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
        return validators.url(url)

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
        
        # Loop through queue
        for url in self.queue:
            print('-'*10, 'STARTING TO CONSIDER THE URL', '-'*10)
            print(url)
             
            # Base url for convert from relative to absolute url
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/')+1] if '/' in parts.path else url

            # Set connection and receive bs4 object
            soup = self.set_connection(url)
            if soup is None:
                continue
            
            # Save all urls which are extracted from HTML of given urls
            # Convert relative url like: 
            # /binh-duong/thi-xa-thuan-an/mua-ban-xe-tai-xe-ben/68893128.htm 
            # to absolute url 
            local_urls = []
            for link in soup.find_all('a'):    
                # extract link url from the anchor    
                anchor = link.attrs["href"] if "href" in link.attrs else ''
                if anchor.startswith('/'):        
                    local_link = base_url + anchor        
                    local_urls.append(local_link)    
                elif strip_base in anchor:        
                    local_urls.append(anchor)    
                elif not anchor.startswith('http'):        
                    local_link = path + anchor        
                    local_urls.append(local_link)    

            # Loop through the document to check post url
            print("Number of links which are retreived from url:", len(local_urls))
            temp_list = local_urls.copy()
            for child_url in temp_list:
                self.check_if_url_is_post(child_url)
                local_urls.remove(child_url)
            print("-- NUMBER OF CRAWLED POST URLS =", self.post_count)

            print('-'*10, 'FINISHING TO CONSIDER THE URL', '-'*10)
            print("")

            # Set number of of urls that you would like to crawl, the number of urls 
            # may be higher because we set it here
            if self.post_count >= NUM_URLS:
                break
        
        print('CRAWLING DONE')

    def save_tocsv(self):
        """
        Save to csv, but it is not recommended
        """
        dic = {"Links": self.result, "HTML": self.html}
        data = pd.DataFrame(dic)
        data.to_csv('post_urls_1.csv')
        print('TASK DONE')

    def save_to_elasticsearch(self, url, html):
        """
        Save page source to ElasticSearch
        """
        h = hashlib.md5(url.encode()).hexdigest()
        if not self.es.exists(index='urls', id=h, doc_type='_doc'):
            doc = {
            'url': url,
            'document': str(html),
            'status': 1,
            'crawledDate': datetime.now(),
            }
            self.es.index(index="urls", id=h, body=doc, doc_type='_doc')
            
