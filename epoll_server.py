import os
import time

import errno
import select
import socket

import traceback

from handlers import get_client


class TimerEvent(object):
    def __init__(self, call_back_time, call_back_func):
        self.call_back_time = call_back_time
        self.call_back_func = call_back_func


class EpollServer(object):
    def __init__(self, svr_sock, client_type, max_fd=10240, time_out=1, max_event=-1):
        self.max_fd = max_fd
        self.time_out = time_out
        self.max_event = max_event

        self._svr = svr_sock
        self._epoll = self._get_epoll()
        self._client_list = {}
        self._timer_list = []
        self._run = True

        self._client_type = client_type

    def _get_epoll(self):
        epoll = select.epoll(self.max_fd)
        epoll.register(self._svr.fileno(), select.EPOLLIN | select.EPOLLET | select.EPOLLHUP)
        return epoll

    def _accept(self):
        conn, _ = self._svr.accept()
        conn.setblocking(False)
        client = get_client(self._client_type, conn)

        self._epoll.register(conn.fileno(), select.EPOLLIN | select.EPOLLOUT | select.EPOLLET | select.EPOLLHUP)
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

    def _handle(self, fd):
        # true for close socket
        try:
            handle = self._client_list[fd]
            while True:
                if handle.handle():
                    # handle can close by return true
                    return True

        except socket.error, ex:
            if ex.errno == errno.EAGAIN:
                return False
            else:
                raise ex

    def _process_events(self):
        event_list = self._epoll.poll(self.time_out, self.max_event)

        for fd, event in event_list:
            if fd == self._svr.fileno():
                self._accept()
                continue

            if event & select.EPOLLHUP:
                self._remove(fd)
                continue

            if event & select.EPOLLIN or event & select.EPOLLOUT:
                close_socket = self._handle(fd)
                if close_socket:
                    self._remove(fd)

    def stop(self):
        self._run = False

    def forever(self):
        while self._run:
            try:
                self._process_timers()
                self._process_events()
            except:
                print os.getpid(), traceback.print_exc()
