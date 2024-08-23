# -*- coding: UTF-8 -*-
import websockets
import json
import logging

logger = logging.getLogger('sspace.socketsort')

async def wsLess(a: str, b: str, sock: websockets.WebSocketServerProtocol, cache: dict[str]) -> bool:
    logger.debug(f"Sorting [{a:s}] < [{b:s}].")
    if a == b:
        logger.debug("Shortcutting comparison of equal values.")
        return False # Equal is not less than.
    first, second = min(a, b), max(a, b)
    if first in cache:
        if second in cache[first]:
            answer = cache[first][second] == a
            logger.debug(f"Returning cached answer: {answer}")
            cache['\x10STATS']['from-cache'] += 1 
            return answer
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
    answer = mesg['answer'] == 'a'
    if first not in cache:
        cache[first] = {}
    cache[first][second] = a if answer else b
    cache['\x10STATS']['interactive'] += 1
    return answer

async def wsPartition(data: list[str], low: int, high: int, sock: websockets.WebSocketServerProtocol, cache: dict[str]) -> int:
    pivot_value = data[low]
    left = low - 1
    right = high + 1

    while True:
        left += 1
        while await wsLess(data[left], pivot_value, sock, cache):
            left += 1
        
        right -= 1
        while await wsLess(pivot_value, data[right], sock, cache):
            right -= 1

        if left >= right:
            return right
        
        data[left], data[right] = data[right], data[left]

async def wsQuicksort(data: list[str], low: int, high: int, sock: websockets.WebSocketServerProtocol, cache: dict[str] = None) -> None:
    if type(cache) != dict:
        cache = {}
    if '\x10STATS' not in cache:
        cache['\x10STATS'] = {
            'interactive': 0,
            'from-cache': 0
        }
    if low < high:
        partition_index = await wsPartition(data, low, high, sock, cache)
        await wsQuicksort(data, low, partition_index, sock, cache)
        await wsQuicksort(data, partition_index + 1, high, sock, cache)