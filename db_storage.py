import sqlite3

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
        if 'c' in locals():  # 检查c是否已经被初始化
            c.close()        # 确保游标被关闭
    return conn

def store_page(url, content, conn):
    try:
        c = conn.cursor()
        c.execute("INSERT INTO pages (url, content) VALUES (?, ?)", (url, content))
        conn.commit()
    except sqlite3.Error as e:
        print(f"An error occurred: {e}")
    finally:
        if 'c' in locals():  # 检查c是否已经被初始化
            c.close()        # 确保游标被关闭

# 使用示例
if __name__ == "__main__":
    conn = init_db()
    store_page("https://www.58pic.com", "<html>Example content</html>", conn)
    conn.close()