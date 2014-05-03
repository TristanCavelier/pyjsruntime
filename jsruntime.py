# -*- coding: utf-8 -*-

# Python library to code as in javascript runtime
# Version 0.1.0
#
# Copyright (c) 2014 Tristan Cavelier <t.cavelier@free.fr>
# This program is free software. It comes without any warranty, to
# the extent permitted by applicable law. You can redistribute it
# and/or modify it under the terms of the Do What The Fuck You Want
# To Public License, Version 2, as published by Sam Hocevar. See
# the COPYING file for more details.

from events import EventEmitter

import threading
import inspect
import time
#import sys
import uuid

"""A Python module to code as in Javascript runtime
"""

class Worker(EventEmitter):
    def __init__(self):
        self._lock = threading.Lock()

    def post_message(self):
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
    #         self.set_immediate(l, *args, **kwargs)

    def _run_if_necessary(self):
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

    # def set_immediate(self, action, *args, **kwargs):
    #     if not inspect.isfunction(action):
    #         raise TypeError('action must be a function')

    #     self._lock.acquire()
    #     self._actions.insert(0, {
    #         "action": action,
    #         "args": args,
    #         "kwargs": kwargs
    #     })
    #     self._run_if_necessary()
    #     self._lock.release()

    def set_timeout(self, action, *args, **kwargs):
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

        def action_wrapper(*args, **kwargs):
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
                "action": action_wrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._run_if_necessary()
            self._lock.release()
            return ref

        # if timeout != 0
        def set_timeout_wrapper():
            self._lock.acquire()
            self._actions.append({
                "action": action_wrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._run_if_necessary()
            self._lock.release()

        self._lock.acquire()
        # add timer object
        timer = threading.Timer(timeout, set_timeout_wrapper)
        self._timeout_timers[ref] = timer
        timer.start()
        self._lock.release()
        return ref

    def clear_timeout(self, ref):
        self._lock.acquire()
        if self._timeout_timers.get(ref) is None:
            self._lock.release()
            return
        if getattr(self._timeout_timers[ref], "cancel", None) is not None:
            self._timeout_timers[ref].cancel()
        del self._timeout_timers[ref]
        self._lock.release()

    def set_interval(self, action, *args, **kwargs):
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
            def action_wrapper(*args, **kwargs):
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
                    "action": action_wrapper,
                    "args": args,
                    "kwargs": kwargs
                })
                self._lock.release()

            self._lock.acquire()
            self._interval_timers[ref] = 1
            self._actions.append({
                "action": action_wrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._run_if_necessary()
            self._lock.release()
            return ref

        # if interval != 0
        def set_interval_wrapper():
            def action_wrapper(*args, **kwargs):
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
                    timer = threading.Timer(last[0] - now, set_interval_wrapper)
                    self._interval_timers[ref] = timer
                    timer.start()
                else:
                    # interval seams already reached so add action directly
                    self._interval_timers[ref] = 1
                    self._actions.append({
                        "action": action_wrapper,
                        "args": args,
                        "kwargs": kwargs
                    })
                self._lock.release()
            self._lock.acquire()
            self._actions.append({
                "action": action_wrapper,
                "args": args,
                "kwargs": kwargs
            })
            self._run_if_necessary()
            self._lock.release()

        self._lock.acquire()
        # add timer object
        last = [time.time() + interval]
        timer = threading.Timer(interval, set_interval_wrapper)
        self._interval_timers[ref] = timer
        timer.start()
        self._lock.release()
        return ref

    def clear_interval(self, ref):
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

    def post_message(self, message):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")
        # get scheduler parent
        parent = getattr(sched, "_parent", None)
        if parent is None: return
        parent.post_message(message)

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

        def post_message_main(message):
            worker_sched._lock.acquire()
            listeners = worker_sched.listeners('message')
            worker_sched._lock.release()
            for l in listeners:
                worker_sched.set_timeout(l, 0, message)

        def post_message_parent(message):
            w._lock.acquire()
            listeners = w.listeners('message')
            w._lock.release()
            for l in listeners:
                sched.set_timeout(l, 0, message)

        w.post_message = post_message_main
        parent.post_message = post_message_parent

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
        worker_sched.set_timeout(wrapper, 0, *args, **kwargs)
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
        sched.set_timeout(wrapper, 0, *args, **kwargs)

    def _set_timer(self, timertype, action, *args, **kwargs):
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
        # if timertype == "immediate":
        #     return sched.set_immediate(wrapper, *args, **kwargs)
        if timertype == "timeout":
            return sched.set_timeout(wrapper, *args, **kwargs)
        if timertype == "interval":
            return sched.set_interval(wrapper, *args, **kwargs)

    def _clear_timer(self, timertype, *args, **kwargs):
        # get scheduler
        self._lock.acquire()
        sched = self._threads.get(threading.current_thread().name)
        self._lock.release()
        if sched is None: raise RuntimeError("Not in js runtime")
        if timertype == "timeout":
            return sched.clear_timeout(*args, **kwargs)
        if timertype == "interval":
            return sched.clear_interval(*args, **kwargs)

    def set_immediate(self, *args, **kwargs):
        return self._set_timer("immediate", *args, **kwargs)

    def set_timeout(self, *args, **kwargs):
        return self._set_timer("timeout", *args, **kwargs)

    def clear_timeout(self, *args, **kwargs):
        return self._clear_timer("timeout", *args, **kwargs)

    def set_interval(self, *args, **kwargs):
        return self._set_timer("interval", *args, **kwargs)

    def clear_interval(self, *args, **kwargs):
        return self._clear_timer("interval", *args, **kwargs)

try: set_timeout
except NameError:
    _manager = JSSchedulerManager()
    add_listener = _manager.add_listener
    on = add_listener
    remove_listener = _manager.remove_listener
    post_message = _manager.post_message
    worker = _manager.worker
    run = _manager.run
    set_timeout = _manager.set_timeout
    clear_timeout = _manager.clear_timeout
    set_interval = _manager.set_interval
    clear_interval = _manager.clear_interval
    set_immediate = _manager.set_immediate
    del _manager
