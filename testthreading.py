import threading
import logging
import time
import concurrent.futures as cf
from datetime import datetime, timedelta

logging.basicConfig(format='%(asctime)s: %(message)s', level=logging.DEBUG, datefmt='%H:%M:%S')


def delayed_task(name, delay):
    logging.info(f'Delayed Thread {name}: Starting thread...')
    time.sleep(delay)
    logging.info(f'Delayed Thread {name}: Finishing thread...')

def immediate_task(name):
    logging.info(f'Immediate Thread {name}: Starting thread...')
    logging.info(f'Immediate Thread {name}: Finishing thread...')

def blocking_task(name):
    logging.info(f'Blocking Thread {name}: Starting thread...')
    start = datetime.now()
    while datetime.now() < start + timedelta(seconds=5):
        pass
    logging.info(f'Blocking Thread {name}: Finishing thread...')

def count_task(counter, name):
    logging.info(f'{name}:     Starting thread...')
    logging.info(f'{name}:     Before counting.')
    counter.count(name) # idling...
    logging.info(f'{name}:     After counting.')
    logging.info(f'{name}:     Ending thread...')

class Counter:
    def __init__(self):
        logging.info(f'M:         Instantiating Counter...')
        self.value = 0
        logging.debug(f'M:         Before instantiating Lock.')
        self._lock = threading.Lock() # idling... # Declared at main thread level - before threading starts.

    def count(self, name):
        logging.debug(f'{name}:         Before acquiring lock.')
        with self._lock: # idling...
            logging.debug(f'{name}:         After acquiring lock.')
            current_value = self.value
            new_value = current_value + 1
            logging.info(f'{name}:         Going into sleep...')
            time.sleep(0.2) # idling...
            logging.info(f'{name}:         Back from sleep...')
            self.value = new_value
            logging.debug(f'{name}:         Before releasing lock.')
            
        logging.debug(f'{name}:         After releasing lock.')
        
    
def main():
    logging.info(f'M: Starting program...')
    logging.info(f'M: Starting main thread...')
    counter = Counter()
    with cf.ThreadPoolExecutor(max_workers=3) as executor:
        for i in range(1,3):
            logging.info(f'M: Before sub-thread {i}.')
            executor.submit(count_task, counter, i)
            logging.info(f'M: After sub-thread {i}.')
    
    logging.info(f'M: Continuing main thread...')
    logging.info(f'M: Finishing program...')
    print(counter.value)

main()

# Main thread (parent) and derivetive thread (child) 
# Upon idle on current child thread, lock is released from the thread and placed back onto the parent thread which then is placed on the next child thread (if there is any) while the previous child thread is still idle (lock is placed back onto the previous child thread when the idle stops).
# at Lock.acquire(), thread acquires the lock.
# At following thread's lock.acquire(), thread waits until previously held lock is released at lock.release().
# at lock.release(), processor goes back to thread that is waiting at lock.acquire()

# lock.acquire(): If lock is free, current thread acquires lock and proceed.
#                 If lock is held by other thread, current thread waits until lock is free again.
# lock.release(): Lock is released.
