import socket
import threading
import sys


class Client(threading.Thread):
    def __init__(self, url, host, port):
        super().__init__()
        self.url = url
        self.host = host
        self.port = port

    def run(self):
        try:
            with socket.create_connection((self.host, self.port)) as sock:
                sock.sendall(self.url.encode('utf-8'))
                response = sock.recv(4096).decode('utf-8')
                print(f"URL: {self.url} -> Ответ: {response}")
        except Exception as e:
            print(f"Ошибка при обработке URL {self.url}: {e}")


def read_urls(file_path):
    with open(file_path, 'r') as file:
        urls = [line.strip() for line in file if line.strip()]
    return urls


def main(file_path, num_threads):
    urls = read_urls(file_path)
    threads = []
    for url in urls:
        client = Client(url, 'localhost', 8000)
        client.start()
        threads.append(client)

        if len(threads) >= num_threads:
            for thread in threads:
                thread.join()
            threads = []
    for thread in threads:
        thread.join()


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Использование: python client.py <файл с URL> <число потоков>")
        sys.exit(1)

    file_path = sys.argv[1]
    num_threads = int(sys.argv[2])
    main(file_path, num_threads)
