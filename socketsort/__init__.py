# -*- coding: UTF-8 -*-
import websockets
import json
import logging

logger = logging.getLogger('sspace.socketsort')

async def wsLess(a: str, b: str, sock: websockets.WebSocketServerProtocol) -> bool:
    logger.debug(f"Sorting [{a:s}] < [{b:s}].")
    await sock.send(json.dumps({
        'type': 'compare',
        'a': a,
        'b': b
    }))
    logger.debug("Compare payload sent to socket.")
    mesg = json.loads(await sock.recv())
    logger.debug("Answer payload received.")
    if mesg['type'] != 'answer':
        logger.error(f"Message type != answer in {mesg!r}")
        raise RuntimeError(f"Received a [{mesg['type']:s}] message when [answer] was expected.")
    if mesg['answer'] not in ['a', 'b']:
        logger.error(f"Answer not in set(a, b) in {mesg!r}")
        raise RuntimeError(f"Received [{mesg['answer']:s}], which is not a valid answer.")
    return mesg['answer'] == 'a'

async def wsPartition(data: list[str], low: int, high: int, sock: websockets.WebSocketServerProtocol) -> int:
    pivot_value = data[high]
    pivot_point = low - 1
    for idx in range(low, high):
        if await wsLess(data[idx], pivot_value, sock):
            pivot_point += 1
            data[pivot_point], data[idx] = data[idx], data[pivot_point]
    pivot_point += 1
    data[pivot_point], data[high] = data[high], data[pivot_point]
    return pivot_point

async def wsQuicksort(data: list[str], low: int, high: int, sock: websockets.WebSocketServerProtocol) -> None:
    if low < high:
        partition_index = await wsPartition(data, low, high, sock)
        await wsQuicksort(data, low, partition_index - 1, sock)
        await wsQuicksort(data, partition_index + 1, high, sock)