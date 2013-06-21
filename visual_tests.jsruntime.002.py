#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsruntime import setInterval, clearInterval, setScript

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        print(threading.current_thread().name, '\t(sleep',
              str(time.time() - last[0])[:5],
              'seconds)', '\t', *args)
        last[0] = time.time()

    print("""Expected output:
    __main__ (sleep 0 s) started
    __main__ (sleep 1 s) a
    __main__ (sleep 1 s) a
    __main__ (sleep 1 s) a
    __main__ (sleep 1 s) a
    """)
    def w():
        tprint('started')
        b = None
        i = [0]
        def a():
            tprint('a')
            time.sleep(0.5)
            if i[0] < 3:
                i[0] += 1
            else:
                clearInterval(b)
        b = setInterval(a, 1)
    setScript(__name__, w)
