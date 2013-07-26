# -*- coding: utf-8 -*-

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
