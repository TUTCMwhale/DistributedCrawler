import time
from kafka import KafkaProducer
import redis

# 选择使用 Kafka 或 Redis
use_kafka = True

if use_kafka:
    producer = KafkaProducer(bootstrap_servers=['localhost:9092'])
else:
    r = redis.Redis(host='localhost', port=6379, db=0)

def produce_urls():
    base_url = "https://www.58pic.com"
    for i in range(100):
        url = f"{base_url}{i}"
        if use_kafka:
            producer.produce('urls', url.encode('utf-8'))
        else:
            r.rpush('urls', url)
        time.sleep(0.1)  # 模拟生成速度

if __name__ == "__main__":
    produce_urls()