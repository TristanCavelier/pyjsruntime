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


from jsruntime import setTimeout, clearTimeout

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
    __main__ (sleep 0 s)   started
    __main__ (sleep 0 s)   a one
    __main__ (sleep 1 s)   a two
    __main__ (sleep 0.5 s) b
    """)
    def w():
        tprint('started')
        i = [0]
        def a(ap):
            tprint('a', ap)
            i[0] = setTimeout(a, 1, 'two')
        def b():
            tprint('b')
            clearTimeout(i[0])
        setTimeout(b, 1.5)
        a('one')
    setTimeout(w)
