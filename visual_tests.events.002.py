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
