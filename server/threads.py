from flask import Flask
import threading
import time
import atexit

from utils import data_generator
from data import collect_providers, jsonify

POOL_TIME = 5
flask_app: Flask = None
threads = []


class Thread:
    def __init__(self, store_type, generator, endpoint, timeout=60) -> None:
        self.timeout = timeout
        self.store_type = store_type
        self.generator = generator
        self.lock = threading.Lock()
        self.timer = threading.Timer(0, lambda x: None, ())

        global flask_app
        flask_app.add_url_rule(endpoint, self.view_func, methods=["GET"])

    def view_func(self):
        with self.lock:
            return jsonify(self.store)

    def run(self):
        self.iteration = 1
        while True:
            self.store = self.store_type()
            print(self.__class__.__name__, "iteration", self.iteration)
            self.iteration += 1
            for item in self.generator():
                with self.lock:
                    self.process_item(item)
            time.sleep(self.timeout)

    def process_item(self, item):
        raise NotImplementedError

    def start(self):
        self.timer = threading.Timer(POOL_TIME, self.run, ())
        self.timer.start()


class DataThread(Thread):
    def __init__(self) -> None:
        super().__init__(list, data_generator, "/api/data")

    def process_item(self, item):
        self.store.append(item)


class ProxiesThread(Thread):
    def __init__(self) -> None:
        super().__init__(dict, collect_providers, "/api/proxies")

    def process_item(self, item):
        proxy, request_time = item
        self.store[proxy] = request_time
        self.store = dict(sorted(self.store.items(), key=lambda item: item[1]))


def interrupt():
    for thread in threads:
        thread.timer.cancel()


def create_threads(thread_classes: list):
    for thread_class in thread_classes:
        threads.append(thread_class())
    atexit.register(interrupt)
