# -*- coding: utf-8 -*-

import threading
import time

"""A Python module to code as in Javascript
"""

class Script():
    """A useful event scheduler class managing event received by this or other
    threads.

    Each instance manages its own queue on its own thread, this thread will run
    until the `quit` flag and an event is sent.
    """

    def __init__(self, name=None):
        """Initialize the instance with a name, if no name is given, then the
        thread name will be generated automatically.

        Arguments:
        - `name`: The script/thread name
        """
        self._name = name
        self._semaphore = threading.Semaphore()
        self._quit = False
        self._running = False
        self._to_run = []
        self._event = threading.Event()
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
        return ident

    # def exist(self, ident):
    #     """exist(ident)

    #     Test if the identifier already exists on the current queue

    #     Arguments:
    #     - `ident`: The callback uniq identifier
    #     """
    #     self._semaphore.acquire()
    #     for event in self._to_run:
    #         if event[2] == ident:
    #             self._semaphore.release()
    #             return True
    #     self._semaphore.release()
    #     return False

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
        self._semaphore.release()

    def removeAll(self):
        """removeAll()

        Removes all the callbacks not already called from the script.
        """
        self._semaphore.acquire()
        for i in range(len(self._to_run)):
            self._to_run.pop(0)[3].cancel()
        self._semaphore.release()

    def quit(self):
        """quit()

        Tells the script to stop after the current call
        """
        self._quit = True
        self._event.set()

    # def kill(self):
    #     "Possible but is a really bad thing"
    #     pass

    def run(self):
        """run()

        Runs the script
        """
        while self._running:
            self._event.wait()
            while True:
                self._event.clear()
                if self._quit:
                    self._running = False
                    self.removeAll()
                    break
                self._semaphore.acquire()
                try:
                    to_run = self._to_run[0]
                except IndexError:
                    self._semaphore.release()
                    break
                else:
                    if to_run[0] <= time.time():
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
                    else:
                        self._semaphore.release()
                        break

    def start(self):
        """start()

        Runs the script in another thread if the script is not already running
        """
        self._semaphore.acquire()
        if not self._running and not self._quit:
            self._running = True
            threading.Thread(target=self.run, name=self._name).start()
        self._semaphore.release()


_semaphore = threading.Semaphore()
_scripts = {}

def _setScript(name, callback):
    if _scripts.get(name) is not None:
        raise RuntimeError("The script '" + name + "' is already running")
    s = Script(name)
    _scripts[name] = s
    s.start()
    s.add(callback)
    return s._name

def setScript(name, callback):
    _semaphore.acquire()
    res = _setScript(name, callback)
    _semaphore.release()
    return res

def _quitScript(name):
    if _scripts.get(name) is None:
        return # RuntimeError
    _scripts[name].quit()
    del _scripts[name]

def quit():
    _semaphore.acquire()
    _quitScript(threading.current_thread().name)
    _semaphore.release()

def _setTimeoutOn(name, callback, timeout=0):
    if _scripts.get(name) is None:
        raise RuntimeError("The script '" + name +
                           "' does not exist (anymore).")
    while True:
        try: return _scripts[name].add(callback, timeout)
        except RuntimeError: pass

def setTimeout(callback, timeout=0):
    _semaphore.acquire()
    res = _setTimeoutOn(threading.current_thread().name, callback, timeout)
    _semaphore.release()
    return res

def _clearTimeoutOn(name, ident):
    if _scripts.get(name) is None:
        return
    _scripts[name].remove(ident)

def clearTimeout(ident):
    _semaphore.acquire()
    _clearTimeoutOn(threading.current_thread().name, ident)
    _semaphore.release()

def _setIntervalOn(name, callback, timeout=0):
    if _scripts.get(name) is None:
        raise RuntimeError("The script '" + name +
                           "' does not exist (anymore).")
    try: return _scripts[name].add(callback, timeout, timeout)
    except RuntimeError: pass

def setInterval(callback, timeout=0):
    _semaphore.acquire()
    res = _setIntervalOn(
        threading.current_thread().name, callback, timeout)
    _semaphore.release()
    return res

def clearInterval(ident):
    _semaphore.acquire()
    _clearTimeoutOn(threading.current_thread().name, ident)
    _semaphore.release()

def _setImmediateOn(name, callback, interval=0):
    if _scripts.get(name) is None:
        raise RuntimeError("The script '" + name +
                           "' does not exist (anymore).")
    try: return _scripts[name].add(callback, 0, interval)
    except RuntimeError: pass

def setImmediate(callback, interval=0):
    _semaphore.acquire()
    res = _setImmediateOn(
        threading.current_thread().name, callback, interval)
    _semaphore.release()
    return res

def clearImmediate(ident):
    _semaphore.acquire()
    _clearTimeoutOn(threading.current_thread().name, ident)
    _semaphore.release()
