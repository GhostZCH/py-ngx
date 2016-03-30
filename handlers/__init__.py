from http_handler import HttpHandler


def get_client(client_name, conn):

    client_dict = {
        "http": HttpHandler
    }

    return client_dict[client_name](conn)
