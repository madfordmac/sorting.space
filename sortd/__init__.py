# -*- coding: UTF-8 -*-
import websockets
from socketsort import wsQuicksort
from uuid_extensions import uuid7str
import json
import time
from datetime import timedelta
import logging

logger = logging.getLogger('sspace.sortd')

async def sorter(websocket: websockets.WebSocketServerProtocol) -> None:
    run_id = uuid7str()
    start_time = time.time()
    logger.info(f'Started new sort socket #{run_id:s}.')
    try:
        mesg = json.loads(await websocket.recv())
        if mesg['type'] != 'hello':
            logger.error(f"Message type != hello in {mesg!r}")
            raise RuntimeError(f"Received a [{mesg['type']:s}] message when [hello] was expected.")
        if 'data' not in mesg:
            logger.error(f"Data element not present in {mesg!r}")
            raise RuntimeError("Data element not present in hello message.")
        data = mesg['data']
        if type(data) != list:
            logger.error(f"Data not a list in {mesg!r}")
            raise RuntimeError("Data element not a list in hello message.")
        for element in data:
            if type(element) != str:
                logger.error(f"Data element «{element!r}» not a string.")
                raise RuntimeError("Non-string data element found in hello message.")
        logger.debug(f'Hello message passes validation. {len(data):d} items to sort.')
        await wsQuicksort(data, 0, len(data) - 1, websocket)
    except RuntimeError as e:
        logger.error(f"Runtime exception received from wsQuicksort. Ending run #{run_id:s}.", exc_info=True)
        await websocket.send(json.dumps({
            'type': 'error',
            'message': str(e)
        }))
        return
    except websockets.exceptions.ConnectionClosedOK as e:
        logger.info(f"Client hung up. 👋🏻")
        return
    except websockets.exceptions.ConnectionClosedError as e:
        logger.warning(f"Connection closed unexpectedly: 😞{e!s}")
        return
    await websocket.send(json.dumps({
        'type': 'result',
        'data': data
    }))
    logger.info(f'Successfully finished run #{run_id:s} ' + \
                f'of {len(data):d} items ' + \
                f'in {timedelta(seconds=time.time() - start_time)!s}.')