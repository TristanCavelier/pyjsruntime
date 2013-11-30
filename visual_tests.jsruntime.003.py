#!/usr/bin/env python3
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


from jsruntime import setTimeout, clearTimeout, setImmediate

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
