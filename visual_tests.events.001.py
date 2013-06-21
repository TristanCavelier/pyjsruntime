# -*- coding: utf-8 -*-

from events import EventEmitter

if __name__ == '__main__':
    print("""Expected output:
    a2
    b2
    [<function a at ...>, <function b at ...>]
    b3
    3
    []
    []
    """)
    ee = EventEmitter()
    ee.emit('log', 1)
    def a(p):
        print('a' + repr(p))
    def b(p):
        print('b' + repr(p))
    ee.on('log', a)
    ee.on('log', b)
    ee.emit('log', 2)
    print(ee.listeners('log'))
    ee.removeListener('log', a)
    ee.emit('log', 3)
    ee.on('log', b)
    ee.on('log', b)
    print(EventEmitter.listenerCount(ee, 'log'))
    ee.on('gol', b)
    ee.removeAllListeners('log')
    print(ee.listeners('log'))
    ee.removeAllListeners()
    print(ee.listeners('gol'))
