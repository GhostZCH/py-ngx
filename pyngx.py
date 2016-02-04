import traceback

from config import CONF
from master import Master
from worker import Worker


if __name__ == '__main__':
    try:
        svr = Master(CONF).start()
        if svr:
            Worker(svr, CONF).start()
    except:
        traceback.print_exc()
