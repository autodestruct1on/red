import socket
import threading
import json
from queue import Queue
from urllib.request import urlopen
from urllib.error import URLError
from collections import Counter
import re

class Worker(threading.Thread):
    def __init__(self, task_queue, k):
        super().__init__(daemon=True)
        self.task_queue = task_queue
        self.k = k

    def run(self):
        while True:
            conn, address = self.task_queue.get()
            if conn is None:
                break
            self.handle_connection(conn, address)
            self.task_queue.task_done()

    def handle_connection(self, conn, address):
        with conn:
            try:
                url = conn.recv(1024).decode('utf-8')
                word_count = self.fetch_and_count_words(url)
                result = json.dumps(dict(word_count))
                conn.sendall(result.encode('utf-8'))
            except Exception as error:
                print(f"Ошибка при обработке запроса от {address}: {error}")

    def fetch_and_count_words(self, url):
        try:
            response = urlopen(url)
            text = response.read().decode('utf-8')
            words = re.findall(r'\w+', text.lower())
            return Counter(words).most_common(self.k)
        except URLError as error:
            print(f"Ошибка при запросе URL {url}: {error}")
            return Counter()

class Server:
    def __init__(self, host, port, worker_count, k):
        self.host = host
        self.port = port
        self.worker_count = worker_count
        self.k = k
        self.task_queue = Queue(maxsize=worker_count)

    def start(self):
        print(f"Сервер запущен на {self.host}:{self.port} с {self.worker_count} воркерами.")
        self.workers = [
            Worker(self.task_queue, self.k) for _ in range(self.worker_count)
        ]
        for worker in self.workers:
            worker.start()

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.host, self.port))
            server_socket.listen()
            while True:
                conn, address = server_socket.accept()
                print(f"Подключен клиент: {address}")
                self.task_queue.put((conn, address))

    def stop(self):
        print("Остановка сервера.")
        for _ in range(self.worker_count):
            self.task_queue.put((None, None))  
        self.task_queue.join()
        for worker in self.workers:
            worker.join()

if __name__ == '__main__':
    import sys
    if len(sys.argv) != 5:
        print("Использование: python server.py -w <число воркеров> -k <число топ слов>")
        sys.exit(1)

    worker_count_arg = int(sys.argv[2])
    top_k = int(sys.argv[4])
    SERVER = Server('localhost', 8000, worker_count_arg, top_k)
    try:
        SERVER.start()
    except KeyboardInterrupt:
        SERVER.stop()
