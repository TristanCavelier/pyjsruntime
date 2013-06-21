#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsruntime import setTimeout, clearTimeout, setScript

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        print(threading.current_thread().name, '\t(sleep',
              str(time.time() - last[0])[:5],
              'seconds)', '\t', *args)
        last[0] = time.time()

    print("""Expected Output:
    __main__ (sleep 0 s)   started
    __main__ (sleep 0 s)   a
    __main__ (sleep 1 s)   a
    __main__ (sleep 0.5 s) b
    """)
    def w():
        tprint('started')
        i = [0]
        def a():
            tprint('a')
            i[0] = setTimeout(a, 1)
        def b():
            tprint('b')
            clearTimeout(i[0])
        setTimeout(b, 1.5)
        a()
    setScript(__name__, w)
