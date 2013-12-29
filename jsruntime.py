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

from events import EventEmitter

import threading
import inspect
import time
import sys
import uuid

"""A Python module to code as in Javascript runtime
"""

class Worker(EventEmitter):
    def __init__(self):
        self._lock = threading.Lock()

    def postMessage(self):
        raise RuntimeError("This method should be overriden")

class JSScheduler(EventEmitter):

    def __init__(self):
        self._lock = threading.Lock()
        self._actions = []
        self._timeout_timers = {}
        self._interval_timers = {}
        self._running = False

    # # override
    # def emit(self, event, *args, **kwargs):
    #     for l in self.listeners(event):
    #         self.setImmediate(l, *args, **kwargs)

    def _runIfNecessary(self):
        if self._running:
            return

        def loop():
            self._lock.acquire()
            while self._actions != []:
                a = self._actions.pop(0)
                self._lock.release()
                try: a["action"](*a["args"], **a["kwargs"])
                except Exception as e:
                    def raisee(): raise e
                    threading.Timer(0, raisee).start()
                    #sys.stderr.write(repr(e) + "\n")
                self._lock.acquire()
            self._running = False
            self._lock.release()

        self._running = True
        threading.Timer(0, loop).start()

    def setImmediate(self, action, *args, **kwargs):
        if not inspect.isfunction(action):
            raise TypeError('action must be a function')

        self._lock.acquire()
        self._actions.insert(0, {
            "action": action,
            "args": args,
            "kwargs": kwargs
        })
        self._runIfNecessary()
        self._lock.release()

    def setTimeout(self, action, *args, **kwargs):
        if not inspect.isfunction(action):
            raise TypeError('action must be a function')

        # get timeout
        if args == ():
            timeout = 0
        else:
            timeout = args[0]
            # XXX check timeout type (must be a number)
            args = args[1:]

        ref = uuid.uuid4()

        def actionWrapper(*args, **kwargs):
            self._lock.acquire()
            if self._timeout_timers.get(ref) is None:
                self._lock.release()
                return
            # remove timer object
            del self._timeout_timers[ref]
            self._lock.release()
            # run action
            action(*args, **kwargs)

        # if timeout = 0
        if timeout == 0:
            self._lock.acquire()
            self._timeout_timers[ref] = 1
            self._actions.append({
                "action": actionWrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._runIfNecessary()
            self._lock.release()
            return ref

        # if timeout != 0
        def setTimeoutWrapper():
            self._lock.acquire()
            self._actions.append({
                "action": actionWrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._runIfNecessary()
            self._lock.release()

        self._lock.acquire()
        # add timer object
        timer = threading.Timer(timeout, setTimeoutWrapper)
        self._timeout_timers[ref] = timer
        timer.start()
        self._lock.release()
        return ref

    def clearTimeout(self, ref):
        self._lock.acquire()
        if self._timeout_timers.get(ref) is None:
            self._lock.release()
            return
        if getattr(self._timeout_timers[ref], "cancel", None) is not None:
            self._timeout_timers[ref].cancel()
        del self._timeout_timers[ref]
        self._lock.release()

    def setInterval(self, action, *args, **kwargs):
        if not inspect.isfunction(action):
            raise TypeError('action must be a function')

        # get interval
        if args == ():
            interval = 0
        else:
            interval = args[0]
            # XXX check interval type (must be a number)
            args = args[1:]

        ref = uuid.uuid4()
        # if interval = 0
        if interval == 0:
            def actionWrapper(*args, **kwargs):
                self._lock.acquire()
                if self._interval_timers.get(ref) is None:
                    self._lock.release()
                    return
                self._lock.release()
                # run action
                action(*args, **kwargs)
                # launch new timer
                self._lock.acquire()
                if self._interval_timers.get(ref) is None:
                    self._lock.release()
                    return
                self._actions.append({
                    "action": actionWrapper,
                    "args": args,
                    "kwargs": kwargs
                })
                self._lock.release()

            self._lock.acquire()
            self._interval_timers[ref] = 1
            self._actions.append({
                "action": actionWrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._runIfNecessary()
            self._lock.release()
            return ref

        # if interval != 0
        def setIntervalWrapper():
            def actionWrapper(*args, **kwargs):
                self._lock.acquire()
                if self._interval_timers.get(ref) is None:
                    self._lock.release()
                    return
                self._lock.release()
                # run action
                action(*args, **kwargs)
                # launch new timer
                self._lock.acquire()
                if self._interval_timers.get(ref) is None:
                    self._lock.release()
                    return
                now = time.time()
                last[0] += interval
                if now < last[0]:
                    # interval not already reached
                    timer = threading.Timer(last[0] - now, setIntervalWrapper)
                    self._interval_timers[ref] = timer
                    timer.start()
                else:
                    # interval seams already reached so add action directly
                    self._interval_timers[ref] = 1
                    self._actions.append({
                        "action": actionWrapper,
                        "args": args,
                        "kwargs": kwargs
                    })
                self._lock.release()
            self._lock.acquire()
            self._actions.append({
                "action": actionWrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._runIfNecessary()
            self._lock.release()

        self._lock.acquire()
        # add timer object
        last = [time.time() + interval]
        timer = threading.Timer(interval, setIntervalWrapper)
        self._interval_timers[ref] = timer
        timer.start()
        self._lock.release()
        return ref

    def clearInterval(self, ref):
        self._lock.acquire()
        if self._interval_timers.get(ref) is None:
            self._lock.release()
            return
        if getattr(self._interval_timers[ref], "cancel", None) is not None:
            self._interval_timers[ref].cancel()
        del self._interval_timers[ref]
        self._lock.release()


class JSSchedulerManager(object):

    def __init__(self):
        self._lock = threading.Lock()
        self._threads = {
            # "Thread name": JSScheduler
        }

    def add_listener(self, event, listener):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        if sched is None:
            self._lock.release()
            raise RuntimeError("Not in js runtime")
        sched.add_listener(event, listener)
        self._lock.release()

    def remove_listener(self, event, listener):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        if sched is None:
            self._lock.release()
            raise RuntimeError("Not in js runtime")
        sched.remove_listener(event, listener)
        self._lock.release()

    def postMessage(self, message):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")
        # get scheduler parent
        parent = getattr(sched, "_parent", None)
        if parent is None: return
        parent.postMessage(message)

    def worker(self, action, *args, **kwargs):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")

        # worker scheduler
        worker_sched = JSScheduler()
        w = Worker()
        parent = Worker()
        worker_sched._parent = parent

        def postMessageMain(message):
            worker_sched._lock.acquire()
            listeners = worker_sched.listeners('message')
            worker_sched._lock.release()
            for l in listeners:
                worker_sched.setImmediate(l, message)

        def postMessageParent(message):
            w._lock.acquire()
            listeners = w.listeners('message')
            w._lock.release()
            for l in listeners:
                sched.setImmediate(l, message)

        w.postMessage = postMessageMain
        parent.postMessage = postMessageParent

        # define wrapper
        def wrapper(*args, **kwargs):
            self._lock.acquire()
            name = threading.current_thread().name
            self._threads[name] = worker_sched
            self._lock.release()

            action(*args, **kwargs)

            self._lock.acquire()
            del self._threads[name]
            self._lock.release()
        worker_sched.setImmediate(wrapper, *args, **kwargs)
        return w

    def run(self, action, *args, **kwargs):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is not None: raise RuntimeError("Already in js runtime")
        sched = JSScheduler()
        # define wrapper
        def wrapper(*args, **kwargs):
            self._lock.acquire()
            name = threading.current_thread().name
            self._threads[name] = sched
            self._lock.release()

            action(*args, **kwargs)

            self._lock.acquire()
            del self._threads[name]
            self._lock.release()
        sched.setImmediate(wrapper, *args, **kwargs)

    def _setTimer(self, timertype, action, *args, **kwargs):
        if not inspect.isfunction(action):
            raise TypeError('action must be a function')
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")
        # define wrapper
        def wrapper(*args, **kwargs):
            self._lock.acquire()
            name = threading.current_thread().name
            self._threads[name] = sched
            self._lock.release()

            try: action(*args, **kwargs)
            except Exception as e:
                def raisee(): raise e
                threading.Timer(0, raisee).start()
                # sys.stderr.write(repr(e) + "\n")

            self._lock.acquire()
            del self._threads[name]
            self._lock.release()
        if timertype == "immediate":
            return sched.setImmediate(wrapper, *args, **kwargs)
        if timertype == "timeout":
            return sched.setTimeout(wrapper, *args, **kwargs)
        if timertype == "interval":
            return sched.setInterval(wrapper, *args, **kwargs)

    def _clearTimer(self, timertype, *args, **kwargs):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")
        if timertype == "timeout":
            return sched.clearTimeout(*args, **kwargs)
        if timertype == "interval":
            return sched.clearInterval(*args, **kwargs)

    def setImmediate(self, *args, **kwargs):
        return self._setTimer("immediate", *args, **kwargs)

    def setTimeout(self, *args, **kwargs):
        return self._setTimer("timeout", *args, **kwargs)

    def clearTimeout(self, *args, **kwargs):
        return self._clearTimer("timeout", *args, **kwargs)

    def setInterval(self, *args, **kwargs):
        return self._setTimer("interval", *args, **kwargs)

    def clearInterval(self, *args, **kwargs):
        return self._clearTimer("interval", *args, **kwargs)

try: setTimeout
except NameError:
    _manager = JSSchedulerManager()
    add_listener = _manager.add_listener
    on = add_listener
    remove_listener = _manager.remove_listener
    postMessage = _manager.postMessage
    worker = _manager.worker
    run = _manager.run
    setTimeout = _manager.setTimeout
    clearTimeout = _manager.clearTimeout
    setInterval = _manager.setInterval
    clearInterval = _manager.clearInterval
    setImmediate = _manager.setImmediate
    del _manager
