#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from jsruntime import setTimeout, clearTimeout, setInterval, \
    clearInterval, setImmediate, clearImmediate, quit, Script, \
    _setScript, _quitScript, setScript
import time
import threading

if __name__ == '__main__':

    def tprint(*args):
        print(time.time(), threading.current_thread().name, *args)

    print("""
    MainThread begin (sleep 1)
    Script b (sleep 3)
    MainThread end
    """)
    tprint('begin')
    def a():
        tprint('a')
    def b():
        tprint('b')
    s = Script('Script')
    s.start()
    i = s.add(a, 3)
    s.add(a, 7)
    s.add(b, 1)
    time.sleep(2)
    s.remove(i)
    time.sleep(2)
    s.quit()
    tprint('end')

    print("""
    started
    a (sleep 1)
    a (sleep 0.5)
    b (sleep 2.5)
    end
    """)
    def w():
        tprint('started')
        i = [0]
        def a():
            tprint('a')
            i[0] = setTimeout(a, 1)
        def b():
            tprint('b')
            clearTimeout(i[0])
            setTimeout(b, 1)
            quit()
        setTimeout(b, 1.5)
        a()
    setScript('Lol', w)
    time.sleep(4)
    tprint('end')

    print("""
    started (sleep 1)
    a (sleep 1)
    a (sleep 1)
    a (sleep 1)
    a (sleep 2)
    end
    """)
    def w():
        tprint('started')
        b = None
        i = [0]
        def a():
            tprint('a')
            if i[0] < 3:
                i[0] += 1
            else:
                clearInterval(b)
        b = setInterval(a, 1)
    setScript('Lol', w)
    time.sleep(6)
    _quitScript('Lol')
    tprint('end')

    print("""
    a (sleep 1)
    a (sleep 1)
    a (sleep 1)
    a (sleep 2)
    end
    """)
    def w():
        b = None
        i = [0]
        def a():
            tprint('a')
            if i[0] < 3:
                i[0] += 1
            else:
                clearImmediate(b)
        b = setImmediate(a, 1)
    setScript('Lol', w)
    time.sleep(5)
    _quitScript('Lol')
    tprint('end')

    print("""
    started (sleep 1)
    a (sleep 2)
    end
    """)
    def w():
        tprint('started')
        i = None
        def a():
            tprint('a')
            time.sleep(2)
            clearInterval(i)
        i = setInterval(a, 1)
    setScript('Lol', w)
    time.sleep(3)
    _quitScript('Lol')
    tprint('end')
