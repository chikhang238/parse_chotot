import pika, sys, os, json
import re
import pandas as pd
import time
from bs4 import BeautifulSoup

from crawl import CrawlHTML

QUEUE_NAME = "crawled_chotot"


def main():
    connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost',heartbeat=600,
                                       blocked_connection_timeout=300))
    channel = connection.channel()
    channel.queue_declare(queue=QUEUE_NAME)

    def callback(ch, method, properties, body):
        queue = json.loads(body)
        print(" [x] Received %r" % queue)
        crawl = CrawlHTML(list(queue.values()))
        crawl.main()
        #crawl.save_tocsv()

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
