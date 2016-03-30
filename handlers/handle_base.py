class HandlerBase(object):
    def __init__(self, conn):
        self._conn = conn

    def sock(self):
        return self._conn

    def fd(self):
        return self.conn.fileno()

    def close(self):
        self._conn.close()

    def handle(self):
        # return true to close the socket
        raise NotImplementedError()




