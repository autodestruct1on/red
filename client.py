import socket
import threading
from queue import Queue

def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        return [line.strip() for line in file.readlines()]

def send_url_to_server(url, host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((host, port))
            client_socket.sendall(url.encode('utf-8'))
            response = client_socket.recv(4096)
            print(f"Ответ от сервера для {url}:\n{response.decode('utf-8')}")
    except Exception as e:
        print(f"Ошибка при обработке {url}: {e}")

def worker(task_queue, host, port):

    while not task_queue.empty():
        url = task_queue.get()
        send_url_to_server(url, host, port)
        task_queue.task_done()

if __name__ == '__main__':
    HOST = 'localhost'
    PORT = 8000
    NUM_THREADS = 4

    urls = read_urls_from_file('urls.txt')

    task_queue = Queue()
    for url in urls:
        task_queue.put(url)

    threads = []
    for _ in range(NUM_THREADS):
        thread = threading.Thread(target=worker, args=(task_queue, HOST, PORT))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print("Обработка всех URL-адресов завершена.")
