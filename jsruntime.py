# -*- coding: utf-8 -*-

from script import Script
import threading
import time

"""A Python module to code as in Javascript
"""

_semaphore = threading.Semaphore()
_scripts = {}

def _setScript(name, callback):
    if _scripts.get(name) is not None:
        raise RuntimeError("The script '" + name + "' is already running")
    s = Script(name)
    _scripts[name] = s
    s.add(callback)
    return s._name

def setScript(name, callback):
    _semaphore.acquire()
    res = _setScript(name, callback)
    _semaphore.release()
    return res

def _quitScript(name):
    if _scripts.get(name) is None:
        return # or RuntimeError
    _scripts[name].quit()
    del _scripts[name]

def quitScript():
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
