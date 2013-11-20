#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsruntime import setTimeout, clearTimeout, setImmediate

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        t = time.time() - last[0]
        if t < 0.001:
            print(threading.current_thread().name, '\t(sleep 0.000 seconds)',
                  '\t', *args)
        else:
            print(threading.current_thread().name, '\t(sleep',
                  str(t)[:5],
                  'seconds)', '\t', *args)
        last[0] = time.time()

    print("""Expected Output:
    __main__ (sleep 0 s)   started
    __main__ (sleep 0 s)   a
    __main__ (sleep 0 s)   b
    __main__ (sleep 0 s)   c
    """)
    def w():
        tprint('started')
        def a():
            tprint('a')
        def b():
            tprint('b')
        def c():
            tprint('c')
        setTimeout(b)
        setImmediate(a)
        setTimeout(c)
    setTimeout(w)
