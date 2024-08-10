# -*- coding: UTF-8 -*-
import websockets
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
    
    # Serve the socket
    async with websockets.serve(sorter, 'localhost', 9832):
        await asyncio.Future()

if __name__ == '__main__':
    asyncio.run(main())