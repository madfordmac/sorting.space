# -*- coding: UTF-8 -*-
import websockets
import socket
from . import sorter
import asyncio
import logging
from logging.handlers import SysLogHandler
import sys, os

async def main() -> None:
    # Set up logging
    logger = logging.getLogger('sspace')
    logger.setLevel(logging.DEBUG)
    fwn_formatter = logging.Formatter('%(asctime)s : %(name)s[%(process)d] : %(levelname)s :: %(message)s')
    if os.path.exists('/dev/log'):
        syslog = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_LOCAL3)
        syslog.setLevel(logging.INFO)
        syslog.setFormatter(logging.Formatter('%(name)s[%(process)d]: %(message)s'))
        logger.addHandler(syslog)
    else:
        filelg = logging.StreamHandler(open('sortd.log', 'a'))
        filelg.setLevel(logging.INFO)
        filelg.setFormatter(fwn_formatter)
        logger.addHandler(filelg)
    if sys.stdout.isatty():
        handlr = logging.StreamHandler()
        handlr.setLevel(logging.DEBUG)
        handlr.setFormatter(fwn_formatter)
        logger.addHandler(handlr)
    logger.info("👀 Logging started for sortd Websocket daemon.")
    
    # Figure out the socket situation
    fd_count = int(os.getenv('LISTEN_FDS', 0))
    if fd_count > 0: # Starting via systemd.
        sock = socket.socket(fileno=3)
        async with websockets.unix_serve(sorter, path=None, sock=sock):
            logger.info(f'Listening for connections on {sock.getsockname():s}')
            await asyncio.Future()
    else: # No systemd info. Serve ourselves, bound to localhost.
        async with websockets.serve(sorter, 'localhost', 9832):
            logger.info("Listening for connections on ws://localhost:9832")
            await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())