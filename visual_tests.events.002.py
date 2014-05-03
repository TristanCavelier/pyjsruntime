# -*- coding: utf-8 -*-

# Script to do some test for events.py
#
# Copyright (c) 2014 Tristan Cavelier <t.cavelier@free.fr>
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# the COPYING file for more details.


from events import EventEmitter

if __name__ == '__main__':
    print("""Expected output:
    a
    b
    """)
    ee = EventEmitter()
    def a():
        print('a')
        ee.emit('b')
    def b():
        print('b')
    ee.on('a', a)
    ee.on('b', b)
    ee.emit('a')
