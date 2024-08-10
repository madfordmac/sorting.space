# -*- coding: UTF-8 -*-
import websockets
from . import sorter
import asyncio
import logging
from logging.handlers import SysLogHandler
import sys

async def main() -> None:
    # Set up logging
    logger = logging.getLogger('sspace')
    logger.setLevel(logging.DEBUG)
    syslog = SysLogHandler(address='/dev/log', facility=SysLogHandler.LOG_LOCAL3)
    syslog.setLevel(logging.INFO)
    syslog.setFormatter(logging.Formatter('%(name)s[%(process)d]: %(message)s'))
    logger.addHandler(syslog)
    if sys.stdout.isatty():
        handlr = logging.StreamHandler()
        handlr.setLevel(logging.DEBUG)
        handlr.setFormatter(logging.Formatter('%(asctime)s : %(name)s[%(process)d] : %(levelname)s :: %(message)s'))
        logger.addHandler(handlr)
    
    # Serve the socket
    async with websockets.serve(sorter, 'localhost', 9832):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())