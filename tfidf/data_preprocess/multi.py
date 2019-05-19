from multiprocessing import Process, current_process
import time
import sys

def daemon():
    p = current_process()
    print('Starting ', p.name, p.pid)
    sys.stdout.flush()
    time.sleep(2)
    print('Exiting', p.name, p.pid)
    sys.stdout.flush()

def non_daemon():
    p = current_process()
    print('Starting ', p.name, p.pid)
    sys.stdout.flush()
    print('Exiting', p.name, p.pid)
    sys.stdout.flush()


if __name__ == '__main__':
    d = Process(name='daemon', target=daemon)
    d.daemon = True

    n = Process(name='non-daemon', target=non_daemon)
    n.daemon = False

    d.start()
    time.sleep(1)
    n.start()

    d.join()
    n.join()
