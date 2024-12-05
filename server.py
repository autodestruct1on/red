import socket
import threading
import json
from collections import Counter
from urllib.request import urlopen
from urllib.error import URLError
import re


class Worker(threading.Thread):
    def __init__(self, conn, address, k):
        super().__init__()
        self.conn = conn
        self.address = address
        self.k = k

    def run(self):
        try:
            url = self.conn.recv(1024).decode('utf-8')
            word_count = self.fetch_and_count_words(url)
            result = json.dumps(dict(word_count))
            self.conn.sendall(result.encode('utf-8'))
        except Exception as e:
            print(f"Ошибка при обработке URL {url}: {e}")
        finally:
            self.conn.close()

    def fetch_and_count_words(self, url):
        try:
            response = urlopen(url)
            text = response.read().decode('utf-8')
            words = re.findall(r'\w+', text.lower())
            word_count = Counter(words).most_common(self.k)
            return word_count
        except URLError:
            return Counter()


class Server:
    def __init__(self, host, port, worker_count, k):
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.k = k
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

    def start(self):
        print(f"Сервер запущен на {self.host}:{self.port} с {self.worker_count} воркерами.")
        while True:
            conn, address = self.server_socket.accept()
            print(f"Подключён клиент: {address}")
            worker = Worker(conn, address, self.k)
            worker.start()


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 5:
        print("Использование: python server.py -w <число воркеров> -k <число топ слов>")
        sys.exit(1)

    worker_count = int(sys.argv[2])
    k = int(sys.argv[4])
    server = Server('localhost', 8000, worker_count, k)
    server.start()
