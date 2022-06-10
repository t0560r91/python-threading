import queue
import random
import threading
import concurrent.futures
import logging
import time


logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.INFO, datefmt='%H:%M:%S')
logging.getLogger().setLevel(logging.DEBUG)
SENTINEL = object()

class FakeDB:
    def __init__(self):
        self.records = list()

    def write_record(self, msg):
        time.sleep(0.1)
        self.records.append(msg)
        

class Pipeline:
    def __init__(self):
        self.msg_que_ar = queue.Queue()
        self.msg_que = queue.Queue(maxsize=10)
        self.c_lock = threading.Lock()
        self.p_lock = threading.Lock()
    
    def set_msg(self, msg):
        logging.info(f'P: Putting {msg} to que...')
        self.msg_que.put(msg)
        self.msg_que_ar.put(msg)
        logging.info(f'P: New que: {list(self.msg_que.queue)}.')
        
    def get_msg(self):
        msg = self.msg_que.get()
        logging.info(f'C: Got {msg} from que...')
        logging.info(f'C: New que: {list(self.msg_que.queue)}.')
        return msg


def producer(pipeline, event):
    while not event.is_set():
        msg = random.randint(1,101)
        pipeline.set_msg(msg)
    logging.info(f'P: End of Loop.')


def consumer(pipeline, db, event):
    while not event.is_set() or not pipeline.msg_que.empty():
        msg = pipeline.get_msg()
        db.write_record(msg)
    logging.info(f'C: End of Loop.')


if __name__ == '__main__':    
    db = FakeDB()
    pipeline = Pipeline()
    event = threading.Event()
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
        logging.info(f'M: Creating P...')
        executor.submit(producer, pipeline, event)

        logging.info(f'M: Creating C...')
        executor.submit(consumer, pipeline, db, event)

        logging.info(f'M: Sleep...')
        time.sleep(0.1)
        logging.info(f'M: Wake.')

        logging.info(f'M: Setting event...')
        event.set()
        
    print(list(pipeline.msg_que_ar.queue))
    print(db.records)


