# -*- coding: utf-8 -*-

"""A python module to
"""

import threading
import time

class Script():
    """A useful event scheduler class managing event received by this or other
    threads.

    Each instance manages its own queue on its own thread which name will be the
    same as the instance name. This thread will run until the queue is
    empty. Each action rerun the thread if it is not already running.
    """

    def __init__(self, name=None):
        """Initialize the instance with a name, if no name is given, then the
        thread name will be generated automatically.

        Arguments:
        - `name`: The script/thread name
        """
        self._name = name
        self._semaphore = threading.Semaphore()
        self._to_run = []
        self._running = False
        self._event = threading.Event()
        self._end_event = threading.Event()
        self._end_event.set()
        self._ident = 0

    def _nextIdent(self):
        """nextIdent() -> int

        Generate a new callback identifier (like `return i++;`)
        """
        i = self._ident
        self._ident += 1
        return i

    def add(self, callback, timeout=0, interval=None, ident=None):
        """This method is the `_add` method wrapped by a lock and unlock

        See _add.__doc__
        """
        self._semaphore.acquire()
        res = self._add(callback, timeout, interval, ident)
        self._semaphore.release()
        return res

    def _add(self, callback, timeout=0, interval=None, ident=None):
        """_add(callback, timeout=0, interval=None, ident=None) -> int

        Adds a `callback` to the script with `ident` as id after `timeout`
        seconds. If `interval` is set, the callback will be called every
        `interval` seconds.

        Returns a new ident if ident is None else returns ident

        Arguments:
        - `callback`: The callback to call
        - `timeout`: The delay before the call
        - `interval`: The delay before the call
        - `ident`: The uniq identifier of the callback
        """
        event = self._event
        if ident is None:
            ident = self._nextIdent()
        for ev in self._to_run:
            if ev[2] == ident:
                raise RuntimeError("A callback with the same identifier exists")
        if timeout < 0: timeout = 0
        t = time.time() + timeout
        timer = threading.Timer(timeout, event.set)
        self._to_run.append((t, callback, ident, timer, interval))
        self._to_run.sort(key=lambda e: e[0])
        if timeout == 0:
            self._event.set()
        else:
            timer.start()
        self._start()
        return ident

    def remove(self, ident):
        """remove(ident)

        Removes a callback thanks to its identifier from the script if this
        callback is not already called.

        Arguments:
        - `ident`: The callback uniq identifier
        """
        self._semaphore.acquire()
        for i in range(len(self._to_run)):
            if self._to_run[i][2] == ident:
                self._to_run.pop(i)[3].cancel()
                break
        self._event.set()
        self._semaphore.release()

    def _removeAllTimers(self):
        """_removeAllTimers()

        Removes all the callbacks not already called from the script.
        """
        for i in range(len(self._to_run)):
            self._to_run.pop(0)[3].cancel()
        self._event.set()

    def quit(self):
        """quit()

        Tells the script to stop after the current call
        """
        self._semaphore.acquire()
        self._removeAllTimers()
        self._semaphore.release()

    # def kill(self):
    #     "Possible but is a really bad thing"
    #     pass

    def run(self):
        """run()

        Runs the script
        """
        self._semaphore.acquire()
        self._running = True
        while self._running:
            if self._to_run == []:
                self._running = False
                self._end_event.set()
                self._semaphore.release()
                break
            self._semaphore.release()
            self._event.wait()
            while True:
                self._event.clear()
                self._semaphore.acquire()
                try:
                    to_run = self._to_run[0]
                except IndexError: break
                if to_run[0] > time.time():
                    break
                self._to_run.pop(0)
                if to_run[4] is not None:
                    self._add(
                        to_run[1],
                        max(to_run[0] - time.time() + to_run[4], 0),
                        to_run[4],
                        to_run[2]
                    )
                self._semaphore.release()
                to_run[1]()
        self._semaphore.release()

    def _start(self):
        """_start()

        Runs the script in another thread if the script is not already running
        """
        # self._semaphore.acquire()
        if not self._running:
            self._end_event.clear()
            threading.Thread(target=self.run, name=self._name).start()
        # self._semaphore.release()
