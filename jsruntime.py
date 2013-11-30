# -*- coding: utf-8 -*-

# Python library to code as in javascript runtime
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

import threading
import time

"""A Python module to code as in Javascript runtime
"""

class JSRuntime(object):

    def __init__(self):
        self._id = 1
        self._lock = threading.Lock()
        self._callbacks = {}
        self._contexts = {}

    def _nextId(self):
        i, self._id = self._id, self._id + 1
        return i

    def getThreadName(self):
        return threading.current_thread().name.split('/')[0]

    def _call(self, i):
        if self._callbacks.get(i) is not None:
            c = self._callbacks[i]
            if not c['keep']:
                del self._callbacks[i]
            self._lock.release()
            c['callback']()
            self._lock.acquire()

    def _addCallback(self, callback, timer, keep=False):
        i = self._nextId()
        self._callbacks[i] = {
            'callback': callback,
            'keep': keep,
            'timer': timer
        }
        return i

    def start(self, name=None):
        if name is None:
            name = self.getThreadName()
        def loop():
            self._lock.acquire()
            while self._contexts[name] != []:
                i = self._contexts[name].pop(0)
                self._call(i)
            del self._contexts[name]
            self._lock.release()
        threading.Thread(
            target = loop,
            name = name # + "/" + str(uuid.uuid4())
        ).start()

    def setTimeout(self, callback, timeout=0):
        return self.setTimeoutOn(self.getThreadName(), callback, timeout)

    def setTimeoutOn(self, name, callback, timeout):
        def operate():
            self._lock.acquire()
            if self._contexts.get(name) is not None: # if context exists
                self._contexts[name].append(i)
            else: # if context does not exist
                if self._callbacks.get(i) is not None: # if the callback exists
                    self._contexts[name] = [i]
                    self.start(name)
            self._lock.release()
        timer = threading.Timer(
            timeout if timeout >= 0 else 0,
            operate
        )
        self._lock.acquire()
        i = self._addCallback(callback, timer)
        self._lock.release()
        timer.start()
        return i

    def clearTimeout(self, i):
        self._lock.acquire()
        if self._callbacks.get(i) is not None:
            if self._callbacks[i]['timer'] is not None:
                self._callbacks[i]['timer'].cancel()
            del self._callbacks[i]
        self._lock.release()

    def setInterval(self, callback, interval=0):
        return self.setIntervalOn(self.getThreadName(), callback, interval)

    def setIntervalOn(self, name, callback, interval):
        def operate():
            self._lock.acquire()
            if self._contexts.get(name) is not None: # if context exists
                self._contexts[name].append(i)
            else: # if context does not exist
                if self._callbacks.get(i) is not None: # if the callback exists
                    self._contexts[name] = [i]
                    self.start(name)
            self._lock.release()

        last = [time.time() + interval]
        timer = threading.Timer(
            interval if interval >= 0 else 0,
            operate
        )

        def wrapper():
            self._lock.acquire()
            if self._callbacks.get(i) is not None:
                now = time.time()
                timeout = interval - (now - last[0])
                last[0] = now + (timeout % interval)
                timer = threading.Timer(
                    timeout if timeout >= 0 else 0,
                    operate
                )
                self._callbacks[i]['timer'] = timer
                timer.start()
            self._lock.release()
            callback()

        self._lock.acquire()
        i = self._addCallback(wrapper, timer, keep=True)
        self._lock.release()
        timer.start()
        return i

    def clearInterval(self, i):
        return self.clearTimeout(i) # XXX

    def setImmediate(self, callback):
        self.setImmediateOn(self.getThreadName(), callback)

    def setImmediateOn(self, name, callback):
        self._lock.acquire()
        i = self._addCallback(callback, None)
        if self._contexts.get(name) is not None: # if context exists
            self._contexts[name].insert(0, i)
        else: # if context does not exist
            if self._callbacks.get(i) is not None: # if the callback exists
                self._contexts[name] = [i]
                self.start(name)
        self._lock.release()
        return i

try: setTimeout
except NameError:
    _runtime = JSRuntime()
    setTimeout = _runtime.setTimeout
    clearTimeout = _runtime.clearTimeout
    setInterval = _runtime.setInterval
    clearInterval = _runtime.clearInterval
    setImmediate = _runtime.setImmediate
    del _runtime
