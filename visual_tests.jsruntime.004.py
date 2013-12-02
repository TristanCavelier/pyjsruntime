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

    print("""Expected Output:
    0 (sleep 1)
    1 (sleep 1)
    2
    """)
    def w():
        setTimeout("print('2')", 2)
        setTimeout("print('1')", 1)
        setTimeout("print('0')")
    setTimeout(w)
