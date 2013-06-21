# -*- coding: utf-8 -*-

from events import EventEmitter

if __name__ == '__main__':
    print("""Expected output:
    a
    b
    """)
    ee = EventEmitter()
    def a():
        print('a')
        ee.emit('b')
    def b():
        print('b')
    ee.on('a', a)
    ee.on('b', b)
    ee.emit('a')
