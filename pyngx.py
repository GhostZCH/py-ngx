import os
import traceback

from config import CONF
from master import Master
from worker import Worker


def main():
    if CONF['master.daemon']:
        if os.fork() > 0:
            return

    svr = Master(CONF).start()
    if svr:
        Worker(svr, CONF).start()


if __name__ == '__main__':
    try:
        main()
    except:
        traceback.print_exc()
