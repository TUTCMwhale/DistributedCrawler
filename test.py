import requests
from bs4 import BeautifulSoup
import time
import sqlite3

def fetch_url(url):
    start_time = time.time()
    response = requests.get(url)
    end_time = time.time()
    return end_time - start_time, response.text

def parse_html(html_content):
    start_time = time.time()
    soup = BeautifulSoup(html_content, 'lxml')
    end_time = time.time()
    return end_time, soup

def store_to_db(soup):
    conn = sqlite3.connect('spider_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS pages (url text, content text)''')
    c.execute("INSERT INTO pages (url, content) VALUES (?, ?)", ('test_url', str(soup)))
    conn.commit()
    conn.close()

urls = ['https://www.58pic.com', 'https://www.wikipedia.org/']

for url in urls:
    fetch_time, html = fetch_url(url)
    parse_time, soup = parse_html(html)
    store_to_db(soup)
    print(f"URL: {url}, Fetch Time: {fetch_time}, Parse Time: {parse_time}")