# 大数据项目二 简易分布式爬虫系统实现

## 项目介绍

### 项目核心信息

系统采用分布式架构，可以运行在多个爬虫节点上，每个节点可以独立地抓取网页数据。使用 Kafka 或 Redis 作为消息队列，用于在爬虫节点之间传递 URL 和协调任务。

### 项目地址

https://github.com/TUTCMwhale/DistributedCrawler?tab=readme-ov-file#%E9%A1%B9%E7%9B%AE%E5%9C%B0%E5%9D%80

## 项目分工

| **团队成员** |       **团队成员**       |
| :----------: | :----------------------: |
|    伏铭贤    | 负责项目开发（个人开发） |

## 项目实现

### 技术选型与相关开发文档

#### 编程语言

Python

#### 消息队列

Kafka 或 Redis，用于解耦和异步处理。Kafka 适合大规模分布式系统，而 Redis 更适合较小规模或需要快速读写的场景。

#### 数据库

SQLite 作为轻量级存储解决方案，适用于数据量不大的场景。

#### Web 抓取

Requests 库用于 HTTP 请求，BeautifulSoup 或 Scrapy 用于 HTML 解析。

#### 流处理

Apache Flink（如果使用 Flink）用于流式处理和去重。

#### 文档编写

使用Markdown编写文档。

### 架构设计

#### 场景分析

（1）数据去重

​    确保每个URL只被抓取一次，避免重复抓取相同数据。

（2）数据存储

​    抓取的数据需要存储到数据库中，以便后续分析和使用。

#### 架构设计

（1）爬虫节点

​    负责从消息队列（Kafka或Redis）中获取URL，抓取网页内容，并将结果存储到数据库。后续可以水平扩展以增加更多的爬虫节点，提高抓取能力。

（2）消息队列（Kafka/Redis）

​    用于存储待抓取的URL和协调爬虫节点。Kafka适用于大规模分布式系统，而Redis更适合较小规模或需要快速读写的场景。

（3）数据库存储

​    提供初始化数据库和存储页面数据的功能。使用SQLite作为轻量级存储解决方案，适用于数据量不大的场景。

（4）去重机制

​    通过Flink流式计算实现待爬取URL的去重，确保每个URL只被抓取一次。

（5）错误处理和日志记录

​    在爬虫节点中添加错误处理和日志记录，以提高系统的健壮性。

### 项目代码介绍

#### Crawler.py文件

负责从 Kafka 或 Redis 接收 URL，抓取网页内容并解析，然后将解析后的数据存储到数据库。

```
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
        time.sleep(1) 
```

#### producer.py文件

负责生成初始的 URL 列表。将 URL 发送到 Kafka 或 Redis 消息队列。

```
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
        time.sleep(0.1)
```

#### db_storage.py文件

提供初始化数据库和存储页面数据的功能，使用SQLite数据库进行数据存储。

```
def init_db():
    conn = sqlite3.connect('spider_data.db')
    try:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS pages
                    (url text, content text)''')
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'c' in locals(): 
            c.close()
    return conn

def store_page(url, content, conn):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO pages (url, content) VALUES (?, ?)", (url, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'c' in locals():  
            c.close()
```

## 测试结果

### 测试目的

确保分布式爬虫系统能够正确、高效地抓取数据，并将数据存储到数据库中。

### 测试环境

Python 3.x

Kafka 服务器（如果使用 Kafka 作为消息队列）

Redis 服务器（如果使用 Redis 作为消息队列）

SQLite 数据库（或其他数据库）

网络连接（用于访问目标网站）

### 功能测试

#### 测试用例

（1）测试用例 1：正常网页抓取

​    输入：一组正常网页的 URL。预期输出：网页内容成功抓取并存储到数据库。

（2）测试用例 2：错误网页抓取

​    输入：包含错误网页（如404、500错误）的 URL 列表。预期输出：错误网页不被抓取，系统记录错误信息。

（3）测试用例 3：重复 URL 去重

​    输入：包含重复 URL 的 URL 列表。预期输出：每个 URL 只被抓取一次。

（4）测试用例 4：数据库存储

​    输入：抓取的网页内容。预期输出：内容成功存储到数据库中。

（5）测试用例 5：producer发送 URL

​    输入：生产者脚本运行，发送 URL 到消息队列。预期输出：URL 成功发送到消息队列。

#### 功能测试步骤

（1）运行producer脚本，发送 URL 到消息队列。

（2）启动爬虫节点，从消息队列中获取 URL 并抓取网页。

（3）验证抓取的网页内容是否正确存储到数据库中。

（4）检查是否有重复的 URL 被抓取。

（5）检查系统是否能够处理错误网页（如404、500错误等）。

### 性能测试

#### 性能测试目标

（1）评估爬虫系统在高并发请求下的性能。

（2）确定系统的瓶颈和可优化点。

#### 性能测试步骤

（1）在控制环境中模拟高并发请求，发送大量 URL 到消息队列。

（2）运行爬虫节点，统计抓取速度、成功率和错误率。

（3）记录数据库写入速度和存储效率。

（4）分析系统资源使用情况，包括CPU、内存和网络带宽。

### 测试用例及结果

测试用例可见test.py，测试步骤包括URL 抓取、HTML 解析和数据库存储，并打印每个步骤的耗时。结果如下：

URL: https://www.58pic.com, Fetch Time: 0.28022074699401855, Parse Time: 1740993772.3546896

URL: https://www.wikipedia.org/, Fetch Time: 0.41481494903564453, Parse Time: 1740993772.8275707

## Demo 演示视频 （必填）

项目包括db_storage.py、crawler.py、producer.py和test.py文件。

首先初始化数据库。运行db_storage.py脚本的终端窗口。

然后运行producer.py脚本的终端窗口。生成URL并发送到消息队列。

之后运行crawler.py脚本的终端窗口。展示爬虫从消息队列获取URL、抓取网页内容的过程。

最后检查数据库，确认数据已正确存储。

## 项目总结与反思

### 项目总结与反思

（1）性能瓶颈

​    在高并发情况下，网络IO和数据库写入会成为瓶颈。

（2）错误处理

​    对异常情况的处理还不够完善，如网络请求失败、解析错误等。

（3）资源消耗

​    内存消耗相对较高，需要优化以降低资源占用。

（4）扩展性

​    当前系统扩展性有限，需要进一步设计以支持更多爬虫节点。

### 优化项

（1）连接池扩展

​    增加 MySQL 连接池容量，启用批量插入模式。

（2）解析引擎分级

​    根据页面复杂度选择解析引擎，平衡速度和内存消耗。

（3）分布式扩展方案

​    引入 Kafka 实现跨服务器任务分发，支持水平扩展 Worker 节点。

（4）缓存层添加

​    对频繁访问的 URL 列表启用 Redis 缓存，减少数据库查询。

### 后续架构优化方向

（1）微服务架构

​    将爬虫系统拆分为独立的微服务，如 URL 生成器服务、抓取服务、解析服务和存储服务。

（2）容器化

​    使用 Docker 容器化各个服务，提高系统的可移植性和可扩展性。

（3）云原生支持

​    将系统部署到云平台（如 AWS、Azure、GCP），利用云服务的弹性和自动扩展能力。

（4）机器学习增强

​    利用机器学习模型识别和抓取更有价值的数据，提高数据质量。

### 项目过程中的反思与总结

在项目初期，应更详细地分析需求，明确系统的目标和范围。设计阶段应充分考虑系统的可扩展性、可维护性和性能要求。在编码过程中，应遵循最佳实践，编写可读、可维护的代码。

## 其他补充资料（选填）

无