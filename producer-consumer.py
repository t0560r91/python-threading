import random
import threading
import concurrent.futures
import logging
import time


logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
SENTINEL = object()

class FakeDB:
    def __init__(self):
        self.records = list()

    def write_record(self, msg):
        time.sleep(0.1)
        self.records.append(msg)
        
class Pipeline:
    def __init__(self):
        self.msg = 0
        self.c_lock = threading.Lock()
        self.p_lock = threading.Lock()
        self.c_lock.acquire()
    
    def set_msg(self, msg):
        self.p_lock.acquire()
        self.msg = msg
        self.c_lock.release()
        
    def get_msg(self):
        self.c_lock.acquire()
        msg = self.msg
        self.p_lock.release()
        return msg


def producer(pipeline, name):
    queue = [random.randint(1,101) for _ in range(30)]
    print(queue)
    for msg in queue:
        pipeline.set_msg(msg)

    pipeline.set_msg(SENTINEL)


def consumer(pipeline, db, name):
    msg = 0
    while msg is not SENTINEL:
        msg = pipeline.get_msg()
        if msg is not SENTINEL:
            db.write_record(msg)
        



if __name__ == '__main__':    
    db = FakeDB()
    pipeline = Pipeline()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        executor.submit(producer, pipeline, 'Producer')
        executor.submit(consumer, pipeline, db, 'Consumer')

    print(db.records)


