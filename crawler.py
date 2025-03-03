import time
import requests
from bs4 import HTMLParser
import sqlite3
from db_storage import init_db, store_page
from kafka import KafkaProducer

# 初始化数据库连接
conn = init_db()

# 选择使用 Kafka 还是 Redis
use_kafka = True

if use_kafka:
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
else:
    import redis
    r = redis.Redis(host='localhost', port=6379, db=0)

def fetch_urls():
    global producer
    if use_kafka:
        message = producer.read_messages()
        urls = [msg.decode('utf-8') for msg in message]
    else:
        import redis
        r = redis.Redis(host='localhost', port=6379, db=0)
        urls = r.lrange('urls')

    for url in urls:
        try:
            response = requests.get(url)
            content = response.content
            store_page(url, content, conn)
        except Exception as e:
            print(f"Error fetching {url}: {e}")

def start_crawler():
    while True:
        fetch_urls()
        time.sleep(1)  # 控制爬取频率

if __name__ == "__main__":
    start_crawler()