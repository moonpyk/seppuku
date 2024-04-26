import functools
import logging
import os
import random
import string
from socketserver import TCPServer, StreamRequestHandler


class Handler(StreamRequestHandler):
    def __init__(self, password, request, client_address, server):
        self.password = password
        super().__init__(request, client_address, server)

    def handle(self):
        data = (self.rfile
                .readline()
                .strip()
                .decode('utf8')
                )
        logging.info(f"<{self.client_address}> {data}")

        if data == 'ping':
            self.request.sendall(b"pong")

        elif data.startswith(f'reboot:{self.password}'):
            try:
                with open('/proc/sys/kernel/sysrq', 'w') as sysrq:
                    print('1', file=sysrq)
                with open('/proc/sysrq-trigger', 'w') as systrigg:
                    print('b', file=systrigg)
                self.request.sendall(b"reboot!")

            except Exception as e:
                logging.error("Une erreur est survenue", exc_info=e)
                self.request.sendall(b"error!")

        else:
            self.request.sendall(b"???")

        self.rfile.close()


def random_password(length=12):
    return ''.join(random.choice(
        string.ascii_lowercase + string.ascii_uppercase + string.digits
    ) for _ in range(length))


def main():
    logging.basicConfig(level=logging.INFO)
    host = os.getenv('SEPPUKU_HOST', '0.0.0.0')
    port = int(os.getenv('SEPPUKU_PORT', '55192'))
    password = os.getenv('SEPPUKU_PASSWORD', None)

    if password is None or len(password) == 0:
        password = random_password()
        logging.info("Mot de passe généré \'%s\'", password)

    server = TCPServer(
        (host, port),
        functools.partial(Handler, password)
    )

    try:
        server.serve_forever()
    except (KeyError, KeyboardInterrupt):
        server.shutdown()


if __name__ == '__main__':
    main()
