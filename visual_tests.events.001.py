# -*- coding: utf-8 -*-

# Script to do some test for events.py
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
    ee.removeListener('log', a)
    ee.emit('log', 3)
    ee.on('log', b)
    ee.on('log', b)
    print(EventEmitter.listenerCount(ee, 'log'))
    ee.on('gol', b)
    ee.removeAllListeners('log')
    print(ee.listeners('log'))
    ee.removeAllListeners()
    print(ee.listeners('gol'))
