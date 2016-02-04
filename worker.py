import os
import signal

from epoll_server import EpollServer


class Worker(object):
    def __init__(self, svr, conf):
        self._svr = EpollServer(svr,
                                conf['epoll.max_fd'],
                                conf['epoll.time_out'],
                                conf['epoll.max_event'])

        signal.signal(signal.SIGINT, self.on_signal)
        signal.signal(signal.SIGTERM, self.on_signal)

    def start(self):
        print 'Worker start: pid [%d] ppid[%d]' % (os.getpid(), os.getppid())
        self._svr.forever()

    def on_signal(self, sig, f):
        self._svr.stop()
