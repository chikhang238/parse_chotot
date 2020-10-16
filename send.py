import json
import pika

QUEUE_NAME = "crawled_chotot"


connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue=QUEUE_NAME)
crawled_links = { '1' : "https://www.chotot.com/mua-ban-do-an-thuc-pham-va-cac-loai-khac",
                  '2' : 'https://www.chotot.com/mua-ban-do-dien-tu',
                  '3' : 'https://www.chotot.com/mua-ban-thu-cung',
                  '4': "https://www.chotot.com/viec-lam",
                  '5': "https://www.chotot.com/mua-ban-tu-lanh-may-lanh-may-giat",
                  '6': "https://www.chotot.com/mua-ban-do-dung-me-va-be",
                  '7': "https://www.chotot.com/mua-ban-do-gia-dung-noi-that-cay-canh",
                  '8': "https://www.chotot.com/mua-ban-thoi-trang-do-dung-ca-nhan",
                  '9': "https://www.chotot.com/mua-ban-giai-tri-the-thao-so-thich",
                  '10': "https://www.chotot.com/mua-ban-do-dung-van-phong-cong-nong-nghiep",
                  '11': "https://www.chotot.com/dich-vu-du-lich",
                  '12': "https://www.chotot.com/mua-ban?giveaway=true",
                  '13': "https://www.chotot.com/mua-ban",
                  '14': "https://nha.chotot.com/",
                  '15': "https://xe.chotot.com/"}
#crawled_links = {'3' : 'https://xe.chotot.com/'}

channel.basic_publish(exchange='', routing_key=QUEUE_NAME, body=json.dumps(crawled_links))
print("Sent list of links")
connection.close()