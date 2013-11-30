# -*- coding: utf-8 -*-

# Python library to do parallel task as javascript Workers do
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

"""
"""

from jsruntime import setTimeout
from events import EventEmitter

import threading
import uuid

class Worker(EventEmitter):
    def __init__(self, callback):
        super().__init__()
        self._original_name = threading.current_thread().name
        self._worker_name = None
        self._worker_emitter = EventEmitter()
        def workerPostMessage(message):
            threading.Thread(
                target = lambda: setTimeout(
                    lambda: self.emit('message', self, message)
                ),
                name = self._original_name
            ).start()
        self._worker_emitter.postMessage = workerPostMessage
        event = threading.Event()
        def wrapper(emitter):
            self._worker_name = threading.current_thread().name
            event.set()
            callback(emitter)
        threading.Thread(
            target = lambda: setTimeout(lambda: wrapper(self._worker_emitter)),
            name = "Worker_" + str(uuid.uuid4())
        ).start()
        event.wait()

    def postMessage(self, message):
        threading.Thread(
            target = lambda: setTimeout(
                lambda: self._worker_emitter.emit(
                    'message',
                    self._worker_emitter, message
                )
            ),
            name = self._worker_name
        ).start()

    def terminate(self):
        raise NotImplementedError() # XXX

# if __name__ == '__main__':
#     import time
#     def tprint(*args):
#         print(threading.current_thread().name, *args)

#     def worker(emitter):
#         def onMessage(emitter, message):
#             tprint("Worker recv:", message)
#             emitter.postMessage('Hello from worker!')
#             time.sleep(1)
#         emitter.on('message', onMessage)
#     def main():
#         def onMessage(w, message):
#             tprint("Main recv:", message)
#         w = Worker(worker)
#         w.on('message', onMessage)
#         w.postMessage('Hello from main!')
#         w.postMessage('Hello from main!')
#     setTimeout(main)
