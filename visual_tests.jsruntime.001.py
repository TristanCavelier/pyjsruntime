#!/usr/bin/env python
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


from jsruntime import run, set_timeout, clear_timeout

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        print(threading.current_thread().name + '\t(sleep ' +
              str(time.time() - last[0])[:5] +
              ' seconds)\t' + ' '.join(args))
        last[0] = time.time()

    print("""Expected Output:
    Thread-1 (sleep 0 s)   started
    Thread-1 (sleep 0 s)   a one
    Thread-4 (sleep 1 s)   a two
    Thread-6 (sleep 0.5 s) b
    """)
    def w():
        tprint('started')
        i = [0]
        def a(ap):
            tprint('a', ap)
            i[0] = set_timeout(a, 1, 'two')
        def b():
            tprint('b')
            clear_timeout(i[0])
        set_timeout(b, 1.5)
        set_timeout(a, 0, 'one')
    run(w)
