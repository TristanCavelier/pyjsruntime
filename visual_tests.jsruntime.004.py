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


from jsruntime import run, worker, on, post_message, set_interval, clear_interval

import time
import threading

if __name__ == '__main__':

    last = [time.time()]
    def tprint(*args):
        t = time.time() - last[0]
        if t < 0.001:
            print(threading.current_thread().name + '\t(sleep 0.000 seconds)' +
                  '\t' + ' '.join(args))
        else:
            print(threading.current_thread().name + '\t(sleep ' +
                  str(t)[:5] +
                  ' seconds)\t' + ' '.join(args))
        last[0] = time.time()

    print("""Expected Output:
    Thread-2  (sleep 0   s)   started
    Thread-4  (sleep 0.2 s)   w message: hello from main!
    Thread-5  (sleep 0.5 s)   w message: hello from main again!
    Thread-1  (sleep 0.1 s)   main message: hi from w!
    Thread-6  (sleep 0.2 s)   a
    Thread-7  (sleep 0.5 s)   main message: hi from w again!
    Thread-9  (sleep 0.5 s)   a
    Thread-10 (sleep 0.5 s)   main message: hi from w again!
    Thread-12 (sleep 0.5 s)   a
    Thread-13 (sleep 0.5 s)   main message: hi from w again!
    Thread-15 (sleep 0.5 s)   a
    Thread-16 (sleep 0.5 s)   main message: hi from w again!
    """)
    def w():
        tprint('started')
        def on_message(message):
            tprint('w message: ' + message)
        on("message", on_message)
        b = None
        i = [0]
        def a():
            tprint('a')
            time.sleep(0.5)
            post_message('hi from w again!')
            if i[0] < 3:
                i[0] += 1
            else:
                clear_interval(b)
        b = set_interval(a, 1)
        time.sleep(0.05)
        post_message('hi from w!')
    def main():
        wor = worker(w)
        def on_message(message):
            tprint('main message: ' + message)
        wor.on("message", on_message)
        time.sleep(0.2)
        wor.post_message('hello from main!')
        time.sleep(0.5)
        wor.post_message('hello from main again!')
        time.sleep(0.1)
    run(main)
