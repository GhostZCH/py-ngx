from handle_base import HandlerBase


_TEST_DATA = "HTTP/1.0 200 OK\r\nContent-type :text/plain\r\nContent-length: 1024\r\nConnection: Keep-Alive\r\n\r\n" + '0' * 1024


class HttpHandler(HandlerBase):
    def __init__(self, conn):
        HandlerBase.__init__(self, conn)
        self._buf = ''
        self._send_idx = 0
        self._handle = self._recv

    def handle(self):
        return self._handle()

    def _recv(self):
        self._buf += self._conn.recv(1024)
        if '\r\n\r\n' in self._buf:
            self._send_idx = 0
            self._handle = self._send
        return False

    def _send(self):
        self._send_idx += self._conn.send(_TEST_DATA[self._send_idx:])
        if self._send_idx >= len(_TEST_DATA):
            return True
        return False
