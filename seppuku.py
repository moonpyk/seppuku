#!/usr/bin/python3
# -*- coding: utf-8 -*-

import functools
import logging
import os
import random
import string
import sys
from socketserver import TCPServer, StreamRequestHandler

KEY_PORT = 'SEPPUKU_PORT'
KEY_LISTEN = 'SEPPUKU_LISTEN'
KEY_PASSWORD = 'SEPPUKU_PASSWORD'

DEFAULTS = {
    KEY_LISTEN: '0.0.0.0',
    KEY_PORT: '55192',
    KEY_PASSWORD: None
}

logger = logging.getLogger('seppuku')


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
        logger.info(f"@{self.client_address}: {data}")

        if data == 'ping':
            self.request.sendall(b"pong")

        elif data == f'reboot:{self.password}':
            try:
                # Super filthy reboot
                with open('/proc/sys/kernel/sysrq', 'w') as sysrq:
                    print('1', file=sysrq)

                with open('/proc/sysrq-trigger', 'w') as systrigg:
                    print('b', file=systrigg)

                # This as almost no chances of being sent correctly
                self.request.sendall(b"reboot!")

            except Exception as e:
                logger.error("An error occurred", exc_info=e)
                self.request.sendall(b"error!")

        elif data == f'nicereboot:{self.password}':
            try:
                if os.spawnl(os.P_WAIT, '/usr/sbin/reboot', 'reboot') == 0:
                    self.request.sendall(b"nice reboot!")
                else:
                    logger.error('An error occurred, exit != 0')

            except Exception as e:
                logger.error('An error occurred', exc_info=e)
                self.request.sendall(b'error!')

        else:
            self.request.sendall(b"???")

        self.rfile.close()


def random_password(length=24):
    return ''.join(random.choice(
        string.ascii_lowercase + string.ascii_uppercase + string.digits
    ) for _ in range(length))


def run():
    logging.basicConfig(level=logging.INFO)
    host = os.getenv(KEY_LISTEN, DEFAULTS[KEY_LISTEN])
    port = int(os.getenv(KEY_PORT, DEFAULTS[KEY_PORT]))
    password = os.getenv(KEY_PASSWORD, DEFAULTS[KEY_PASSWORD])

    if password is None or len(password) == 0:
        password = random_password()
        logger.info("Random password generated \"%s\"", password)

    server = TCPServer(
        (host, port),
        functools.partial(Handler, password)
    )

    try:
        logger.info(
            "Listening on %s:%s",
            server.server_address[0],
            server.server_address[1]
        )
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Exiting...")
        server.shutdown()


def main(argv):
    if len(argv) <= 1:
        argv.append("run")

    match argv[1]:
        case "run":
            run()

        case "genconfig":
            for k in DEFAULTS:
                v = DEFAULTS[k] if k != KEY_PASSWORD else random_password()
                print(f'{k}=\"{v}\"')


if __name__ == '__main__':
    main(sys.argv)
