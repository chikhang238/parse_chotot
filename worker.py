import pika, sys, os, json
import re
import requests
import pandas as pd
import time
from bs4 import BeautifulSoup

from crawl import CrawlHTML

BASE_URL = "https://chotot.com"
QUEUE_NAME = "crawled_chotot"


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',heartbeat=600,
                                       blocked_connection_timeout=300))
    channel = connection.channel()

    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        queue = json.loads(body)
        print(" [x] Received %r" % queue)
        # mess = json.loads(body)
        # print(" [x] Received %r" % mess)
        # count_link = 1
        # for idx in mess:
        #     url = mess[idx]
        #     print('----- STARTING TO CRAWL: ', url, '-----')
        #     all_links = list()
        #     urls_put = list()
        #     result = list()
        #     count = 0

        #     while True:
        #         print(url)
        #         try:
        #             req = requests.get(url, timeout = 5)
        #         except:
        #             print("Cannot access this url")

        #             temp = all_links
        #             for each_link in temp:
        #                 if 'htm' in each_link:
        #                     result.append(each_link)
        #                     all_links.remove(each_link)
        #                     count += 1
        #                     print(count)
        #                 else:
        #                     url = each_link
        #                     all_links.remove(each_link)
        #                     break
        #             print('New url:', url)
        #             continue

        #         soup = BeautifulSoup(req.text)
        #         not_full = soup.find_all('a', {'href': re.compile('^/')})
        #         full = soup.find_all('a', {'href': re.compile('^https://')})

        #         page_links = []
        #         for link in not_full:
        #             link = BASE_URL + link['href']
        #             if link not in urls_put: 
        #                 page_links.append(link)
        #                 urls_put.append(link)
        #         for link in full:
        #             link = link['href']
        #             if link not in urls_put and 'chotot' in link: 
        #                 page_links.append(link)
        #                 urls_put.append(link)
        #         print("PAGE:", len(page_links))
        #         all_links = all_links + page_links
        #         temp = all_links[:]
                
        #         for each_link in temp:
        #             if 'htm' in each_link:
        #                 result.append(each_link)
        #                 all_links.remove(each_link)
        #                 count += 1
        #                 print(count)
        #             else:
        #                 url = each_link
        #                 all_links.remove(each_link)
        #                 break
        #         if len(all_links) == 0 or count >= 5000:
        #             break

        #     print(result)
        #     result_df = pd.DataFrame(result, columns = ['Links'])
        #     count_link += 1
        #     result_df.to_csv(str(count_link) + '.csv')
        #     print('----- DONE: ', count_link)
        crawl = CrawlHTML(list(queue.values()))
        crawl.main()
        crawl.save_tocsv()

    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
    print(' [*] Waiting for messages. To exit press CTRL+C')

    channel.start_consuming()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print('Interrupted')
        try:
            #channel.stop_consuming()
            sys.exit(0)
        except SystemExit:
            os._exit(0)