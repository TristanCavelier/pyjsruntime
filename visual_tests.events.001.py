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
    a2
    b2
    [<function a at ...>, <function b at ...>]
    b3
    3
    []
    []
    """)
    ee = EventEmitter()
    ee.emit('log', 1)
    def a(p):
        print('a' + repr(p))
    def b(p):
        print('b' + repr(p))
    ee.on('log', a)
    ee.on('log', b)
    ee.emit('log', 2)
    print(ee.listeners('log'))
    ee.remove_listener('log', a)
    ee.emit('log', 3)
    ee.on('log', b)
    ee.on('log', b)
    print(EventEmitter.listener_count(ee, 'log'))
    ee.on('gol', b)
    ee.remove_all_listeners('log')
    print(ee.listeners('log'))
    ee.remove_all_listeners()
    print(ee.listeners('gol'))
