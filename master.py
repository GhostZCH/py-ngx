import os
import time
import signal
import socket

from epoll_server import EpollServer

_PID_FILE_NAME = 'py-ngx.pid'


class Master(object):
    def __init__(self, conf):
        self._conf = conf
        self._worker = []
        self._run = True

        signal.signal(signal.SIGINT, self.on_signal)
        signal.signal(signal.SIGTERM, self.on_signal)
        signal.signal(signal.SIGCHLD, self.on_signal)
        signal.signal(signal.SIGUSR1, self.on_signal)

        self._svr = None

    def _get_server(self):
        svr = socket.socket()
        svr.bind((self._conf['svr.ip'], self._conf['svr.port']))
        svr.listen(1024)
        return svr

    def start(self):
        self._svr = self._get_server()

        with open(_PID_FILE_NAME, 'w') as pid_file:
            pid_file.write('%s' % os.getpid())

        for i in xrange(self._conf['worker.num']):
            pid = os.fork()
            if pid:
                self._worker.append(pid)
            else:
                return self._svr

        print 'worker list', self._worker

        while self._run:
            time.sleep(1)

        self._clear()
        return None

    def on_signal(self, sig, f):
        print 'get sig[%s]' % sig
        if sig == signal.SIGUSR1:
            self._reload()
        else:
            self._close()

    def _clear(self):
        print 'clear'
        self._svr.close()
        os.remove(_PID_FILE_NAME)
        for cld in self._worker:
            os.kill(cld, signal.SIGTERM)

    def _close(self):
        self._run = False

    def _reload(self):
        self._clear()
        self.start()
