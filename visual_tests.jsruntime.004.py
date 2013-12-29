#!/usr/bin/env python
# -*- coding: utf-8 -*-
# python2 or 3

# Script to do some test for pyjsruntime
# Copyright (C) 2013  Tristan Cavelier <t.cavelier@free.fr>
#
#   This library is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This library is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.


from jsruntime import run, worker, on, postMessage, setInterval, clearInterval

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
            postMessage('hi from w again!')
            if i[0] < 3:
                i[0] += 1
            else:
                clearInterval(b)
        b = setInterval(a, 1)
        time.sleep(0.05)
        postMessage('hi from w!')
    def main():
        wor = worker(w)
        def on_message(message):
            tprint('main message: ' + message)
        wor.on("message", on_message)
        time.sleep(0.2)
        wor.postMessage('hello from main!')
        time.sleep(0.5)
        wor.postMessage('hello from main again!')
        time.sleep(0.1)
    run(main)
