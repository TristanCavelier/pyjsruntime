#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from script import Script

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
    MainThread      (sleep 0 seconds)    started
    __main__        (sleep 1 seconds)    main
    __main__        (sleep 2 seconds)    lol
    __main__        (sleep 0 seconds)    main
    __main__        (sleep 2 seconds)    lol
    MainThread      (sleep 0 seconds)    end
    """)
    def main():
        tprint('main')
        def lol():
            tprint('lol')
        s.add(lol, 2)
    s = Script(__name__)
    tprint('started')
    s.add(main, 1)
    s._end_event.wait()
    s.add(main)
    s._end_event.wait()
    tprint('end')
