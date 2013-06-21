#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsruntime import setTimeout, setScript, _setTimeoutOn

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
    one (sleep 0 s) started
    two (sleep 1 s) started
    two (sleep 1 s) a
    one (sleep 1 s) a
    """)
    def one():
        tprint('started')
        setTimeout(lambda: setScript('two', two), 1)
    def two():
        tprint('started')
        def a():
            tprint('a')
        setTimeout(a, 1)
        _setTimeoutOn('one', a, 2)
    setScript('one', one)
