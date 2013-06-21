#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Compatible with python2 and 3. It provides:

- EventEmitter class, event manager and emitter inspired by
  nodejs 'events' module.

Typically, event names are represented by a camel-cased string, however,
there aren't strict restrictions on that, as any string will be accepted.

Functions can then be attached to objects, to be executed when an event is
emitted. These functions are called listeners.
"""

import sys
import threading

class EventEmitter(object):
    """Inspired by nodejs EventEmitter class
    http://nodejs.org/api/events.html

    When an EventEmitter instance experiences an error, the typical action is
    to emit an 'error' event. Error events are treated as a special case in
    node. If there is no listener for it, then the default action is to raise
    the error again.

    All EventEmitters emit the event 'newListener' when new listeners are added
    and 'removeListener' when a listener is removed.
    """

    def __init__(self):
        """Initialize the EventEmitter
        """
        self._events = {}
        self._warned_events = {}
        self._max_listeners = 10

    def on(self, event, listener):
        """Adds a listener to the end of the listeners array for the specified
        event.

            def onConnection(server, stream):
                print('someon connected!')

            server.on('connection', onConnection)

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        self.emit("newListener", self, event, listener);
        if self._events.get(event) is None:
            self._events[event] = []
        listener_list = self._events[event]
        listener_list.append(listener)
        if self._max_listeners > 0 and \
           len(listener_list) > self._max_listeners and \
           self._warned_events.get(event) is not True:
            sys.stderr.write("warning: possible EventEmitter memory leak " +
                             "detected. " + str(len(listener_list)) + " " +
                             "listeners added. Use emitter.setMaxListeners() " +
                             "to increase limit.\n")
            self._warned_events[event] = True
        return self

    def addListener(self, event, listener):
        """Is equal to emitter.on method.

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        return self.on(event, listener);

    def once(self, event, listener):
        """Adds a one time listener for the vent. This listener is invoked only
        the next time the event is fired, after which it is removed

            def onFirstConnection(server, stream):
                print('Ah, we have our first user!')

            server.once('connection', onFirstConnection)

        Returns emitter, so calls can be chained.

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.removeListener(event, listener)
        self.on(event, wrapper)
        return self

    def removeListener(self, event, listener):
        """Remove a listener from the listener array for the specified event.

            def callback(server, stream):
                print('someone connected!')

            server.on('connection', callback)
            # ...
            server.removeListener('connection', callback)

        Returns emitter, so calls can be chained.

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        if self._events.get(event) is not None:
            try: self._events[event].remove(listener)
            except ValueError: pass
            if self._events[event] == []:
                del self._events[event]
                try: del self._warned_events[event]
                except KeyError: pass
        self.emit("removeListener", self, event, listener)
        return self

    def removeAllListeners(self, event=None):
        """Removes all listeners, or those of the specified event.

        Returns emitter, so calls can be chained.

        Arguments:
        - `event`: The event name (optional)
        """
        if event is None:
            for event in [k for k in self._events.keys()]:
                del self._events[event]
                try: del self._warned_events[event]
                except KeyError: pass
        else:
            del self._events[event]
            try: del self._warned_events[event]
            except KeyError: pass
        return self

    def setMaxListeners(self, max_listeners):
        """By default EventEmitters will print a warning if more than 10
        listeners are added for a particular event. This is a useful default
        which helps finding memory leaks. Obviously not all Emitters should be
        limited to 10. This function allows that to be increased. Set to zero
        for unlimited.

        Arguments:
        - `max_listeners`: The maximum number of listeners
        """
        self._max_listeners = max_listeners

    def emit(self, event, *args, **kwargs):
        """Execute each of the listeners in order with the supplied arguments.

        Returns `True` if event had listeners, `false` otherwise.

        Arguments:
        - `event`: The event name
        - `*args`: The supplied arguments
        - `**kwargs`: The supplied arguments
        """
        if self._events.get(event) is None:
            return False

        listener_list = [x for x in self._events[event]]

        for listener in listener_list:
            listener(*args, **kwargs)

        return True

    def listeners(self, event):
        """Returns an array of listeners for the specified event.

            def onConnection(server, stream):
                print('someone connected!')

            server.on('connection', onConnection)

            print(server.listeners('connection')) # [<function onConnection>]

        Arguments:
        - `event`: The event name
        """
        try: return self._events[event]
        except KeyError: return []

    @staticmethod
    def listenerCount(emitter, event):
        """Return the number of listeners for a given event.
        """
        return len(emitter.listeners(event))
