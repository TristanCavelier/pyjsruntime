#!/usr/bin/env python2
# -*- coding: utf-8 -*-
# python2 or 3

# Script to do some test for pyjsruntime
#
# Copyright (c) 2014 Tristan Cavelier <t.cavelier@free.fr>
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# the COPYING file for more details.


from jsruntime import run, set_interval, clear_interval

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        print(threading.current_thread().name + '\t(sleep ' +
              str(time.time() - last[0])[:5] +
              ' seconds)\t' + ' '.join(args))
        last[0] = time.time()

    print("""Expected output:
    Thread-1 (sleep 0 s) started
    Thread-3 (sleep 1 s) a
    Thread-5 (sleep 1 s) a
    Thread-7 (sleep 1 s) a
    Thread-9 (sleep 1 s) a
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
                clear_interval(b)
        b = set_interval(a, 1)
    run(w)
