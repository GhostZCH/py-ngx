import os
import time
import errno
import socket
import select
import traceback
import multiprocessing

_TEST_DATA = "HTTP/1.0 200 OK\r\nContent-type :text/plain\r\nContent-length: 1024\r\nConnection: Keep-Alive\r\n\r\n" + '0' * 1024


class TimerEvent(object):
    def __init__(self, call_back_time, call_back_func):
        self.call_back_time = call_back_time
        self.call_back_func = call_back_func


class Client(object):
    def __init__(self, conn):
        self.conn = conn

        self.buf = ''
        self.keep_alive = False

        self._send_idx = 0

    def fd(self):
        return self.conn.fileno()

    def recv(self):
        print 'recv'
        try:
            while True:
                tmp = self.conn.recv(1024)
                if not tmp and not self.buf:
                    raise ValueError('Not recv')
                self.buf += tmp

        except socket.error, ex:
            if ex.errno == errno.EAGAIN:
                if '\r\n\r\n' in self.buf:
                    self.keep_alive = 'keep-alive' in self.buf
                    self._send_idx = 0
                    return False
                return True
            else:
                raise ex

    def send(self):
        print 'send'
        try:
            while self._send_idx < len(_TEST_DATA):
                send_len = self.conn.send(_TEST_DATA[self._send_idx:])
                if not send_len:
                    raise ValueError('send failed')

                self._send_idx += send_len

            self.buf = ''
            return False

        except socket.error, ex:
            if ex.errno == errno.EAGAIN:
                return True
            else:
                raise ex

    def close(self):
        print 'close'
        self.conn.close()


class EpollServer(object):
    def __init__(self, svr_sock, max_fd=10240, time_out=1, max_event=-1):
        self.max_fd = max_fd
        self.time_out = time_out
        self.max_event = max_event

        self._svr = svr_sock
        self._epoll = self._get_epoll()
        self._client_list = {}
        self._timer_list = []
        self._run = True

        self._lock = multiprocessing.Lock()

    def _get_epoll(self):
        epoll = select.epoll(self.max_fd)
        epoll.register(self._svr.fileno(), select.EPOLLIN)
        return epoll

    def _accept(self):
        print os.getpid(), 'accept'

        conn, _ = self._svr.accept()
        print os.getpid(), 'accept finish'
        conn.setblocking(False)
        client = Client(conn)

        self._epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLET | select.EPOLLHUP)
        self._client_list[conn.fileno()] = client

    def _remove(self, fd):
        self._epoll.unregister(fd)
        self._client_list[fd].close()
        del self._client_list[fd]

    def _process_timers(self):
        now = time.time()
        for t in self._timer_list:
            if t.call_back_time < now:
                t.call_back_func()

    def _process_events(self):
        with self._lock:
            print os.getpid(), 'poll'
            event_list = self._epoll.poll(self.time_out, self.max_event)
            print os.getpid(), 'poll finish'

        for fd, event in event_list:
            if fd == self._svr.fileno():
                self._accept()
                continue

            if event & select.EPOLLHUP:
                self._remove(fd)
                continue

            if event & select.EPOLLIN:
                again = self._client_list[fd].recv()
                if not again:
                    self._epoll.modify(fd, select.EPOLLOUT | select.EPOLLET | select.EPOLLHUP)
                continue

            if event & select.EPOLLOUT:
                again = self._client_list[fd].send()
                if not again:
                    if self._client_list[fd].keep_alive:
                        self._client_list[fd].modify(fd, select.EPOLLIN | select.EPOLLET | select.EPOLLHUP)
                    else:
                        self._remove(fd)
                continue

    def stop(self):
        self._run = False

    def forever(self):
        while self._run:
            try:
                self._process_timers()
                self._process_events()
            except:
                print os.getpid(), traceback.print_exc()
