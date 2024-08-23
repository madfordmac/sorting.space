# -*- coding: UTF-8 -*-
import websockets
import json
import logging

logger = logging.getLogger('sspace.socketsort')

async def wsLess(a: str, b: str, sock: websockets.WebSocketServerProtocol) -> bool:
    logger.debug(f"Sorting [{a:s}] < [{b:s}].")
    if a == b:
        logger.debug("Shortcutting comparison of equal values.")
        return False # Equal is not less than.
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
    pivot_value = data[low]
    left = low - 1
    right = high + 1

    while True:
        left += 1
        while await wsLess(data[left], pivot_value, sock):
            left += 1
        
        right -= 1
        while await wsLess(pivot_value, data[right], sock):
            right -= 1

        if left >= right:
            return right
        
        data[left], data[right] = data[right], data[left]

async def wsQuicksort(data: list[str], low: int, high: int, sock: websockets.WebSocketServerProtocol) -> None:
    if low < high:
        partition_index = await wsPartition(data, low, high, sock)
        await wsQuicksort(data, low, partition_index, sock)
        await wsQuicksort(data, partition_index + 1, high, sock)