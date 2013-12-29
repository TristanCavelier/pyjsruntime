# -*- coding: utf-8 -*-

# Translated from Nodejs events module (events.js) which is released under the
# MIT license.

# events.js source code and license:
# https://github.com/joyent/node/blob/master/lib/events.js

# Original documentation:
# http://nodejs.org/api/events.html


# Python event management library
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


"""Compatible with python2 and 3. It provides:

- EventEmitter class, event manager and emitter inspired by
  nodejs 'events' module.

Typically, event names are represented by a camel-cased string, however,
there aren't strict restrictions on that, as any string will be accepted.

Functions can then be attached to objects, to be executed when an event is
emitted. These functions are called listeners.
"""

import sys, inspect

class EventEmitter(object):
    """To access to EventEmitter class, `import EventEmitter from events`

    When an `EventEmitter` instance experiences an error, the typical action is
    to emit an `'error'` event. Error events are treated as a special case. If
    there is no listener for it, then the default action is to raise the error.

    All EventEmitters emit the event 'newListener' when new listeners are added
    and 'removeListener' when a listener is removed.
    """

    def __init__(self):
        """Initialize the EventEmitter
        """
        self._events = {}
        self._max_listeners = None

    def add_listener(self, event, listener):
        """Adds a listener to the end of the listeners array for the specified
        event.

            def onConnection(server, stream):
                print('someon connected!')

            server.add_listener('connection', onConnection)

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        if not inspect.isfunction(listener):
            raise TypeError('listener must be a function')

        if not isinstance(getattr(self, "_events", None), dict):
            self._events = {}

        # To avoid recursion in the case that event == "newListener"! Before
        # adding it to the listeners, first emit "newListener".
        if self._events.get("newListener") is not None:
            self.emit("newListener",
                      event,
                      listener.listener if \
                      inspect.isfunction(getattr(listener, 'listener', None)) \
                      else listener)

        if self._events.get(event) is None:
            # Optimize the case of one listener. Don't need the extra array obj
            self._events[event] = listener
        elif isinstance(self._events[event], list):
            # if we've already got an array, just append
            self._events[event].append(listener)
        else:
            # Adding the second element, need to change to array
            self._events[event] = [self._events[event], listener]

        # Check for listener leak
        handler = self._events[event]
        if isinstance(handler, list) and \
           (getattr(self, '_warned_events', None) is None or \
            self._warned_events.get(event) is None):
            if getattr(self, "_max_listeners", None) is not None:
                m = self._max_listeners
            else:
                m = EventEmitter.default_max_listeners

            if m > 0 and len(handler) > m:
                if getattr(self, '_warned_events', None) is None:
                    self._warned_events = {}
                self._warned_events[event] = True
                sys.stderr.write("""warning: possible EventEmitter memory leak \
detected. """ + str(len(listener_list)) + """ listeners added. \
Use emitter.set_max_listeners() to increase limit.\n""")

        return self

    # def on(self, *args, **kwargs):
    #     """Is equal to emitter.add_listener method.

    #     Arguments:
    #     - `event`: The event name
    #     - `listener`: The listener callback
    #     """
    #     return self.add_listener(*args, **kwargs);

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
        if not inspect.isfunction(listener):
            raise TypeError('listener must be a function')

        def g(*args, **kwargs):
            self.remove_listener(event, listener)
            listener(*args, **kwargs)

        g.listener = listener
        self.add_listener(event, g)
        return self

    def remove_listener(self, event, listener):
        """Remove a listener from the listener array for the specified event.

            def callback(server, stream):
                print('someone connected!')

            server.add_listener('connection', callback)
            # ...
            server.remove_listener('connection', callback)

        Returns emitter, so calls can be chained.

        Arguments:
        - `event`: The event name
        - `listener`: The listener callback
        """
        if not inspect.isfunction(listener):
            raise TypeError('listener must be a function')

        if not isinstance(getattr(self, "_events", None), dict) or \
           self._events.get(event) is None:
            return self

        handler = self._events[event]
        length = len(handler) if isinstance(handler, list) else 1
        position = -1

        if handler == listener or \
           (inspect.isfunction(getattr(handler, 'listener', None)) == listener):
            del self._events[event]
            if self._events.get('removeListener') is not None:
                self.emit('removeListener', event, listener)
        elif isinstance(handler, list):
            for i in range(length - 1, -1, -1):
                if handler[i] == listener or \
                   getattr(handler, 'listener', None) == listener:
                    position = i
                    break

            if position < 0: return self

            if length == 1:
                del self._events[event]
            else:
                handler.pop(position)

            if self._events.get('removeListener') is not None:
                self.emit('removeListener', event, listener)

        return self

    def remove_all_listeners(self, *args):
        """Removes all listeners, or those of the specified event.

        Returns emitter, so calls can be chained.

        Arguments:
        - `*args`: [0] The event name (optional)
        """
        if not isinstance(getattr(self, "_events", None), dict): return self

        # not listening for removeListener, no need to emit
        if self._events.get('removeListener') is None:
            if len(args) == 0:
                self._events = {}
            elif self._events[args[0]]:
                del self._events[args[0]]
            return self

        # emit removeListener for all listeners on all events
        if len(args) == 0:
            for key in self._events.keys():
                if key == 'removeListener': continue
                self.remove_all_listeners(key)
            self.remove_all_listeners('removeListener')
            self._events = {}
            return self

        event = args[0]
        listeners = self._events.get(event)

        if inspect.isfunction(listeners):
            self.remove_listener(event, listeners)
        else:
            # LIFO order
            while len(listeners) > 0:
                self.remove_listener(event, listeners[len(listeners) -1])
        del self._events[event]

        return self

    def set_max_listeners(self, n):
        """By default EventEmitters will print a warning if more than 10
        listeners are added for a particular event. This is a useful default
        which helps finding memory leaks. Obviously not all Emitters should be
        limited to 10. This function allows that to be increased. Set to zero
        for unlimited.

        Arguments:
        - `n`: The maximum number of listeners
        """
        if not isinstance(n, int) or n < 0:
            raise TypeError("n must be a positive number")
        self._max_listeners = n
        return self

    def emit(self, event, *args, **kwargs):
        """Execute each of the listeners in order with the supplied arguments.

        Returns `True` if event had listeners, `false` otherwise.

        Arguments:
        - `event`: The event name
        - `*args`: The supplied arguments
        - `**kwargs`: The supplied arguments
        """
        if not isinstance(getattr(self, "_events", None), dict):
            self._events = {}

        if event == "error":
            handler = self._events.get('error')
            if handler is None or \
               (isinstance(handler, list) and len(handler) == 0):
                er = args[0] if len(args) > 0 else None
                if isinstance(er, Exception):
                    raise er # Unhandled 'error' event
                raise TypeError('Uncaught, unspecified "error" event.')

        handler = self._events.get(event)
        if handler is None:
            return False

        if inspect.isfunction(handler):
            handler(*args, **kwargs)
        elif isinstance(handler, list):
            listeners = handler[:]
            for listener in listeners:
                listener(*args, **kwargs)

        return True

    def listeners(self, event):
        """Returns an array of listeners for the specified event.

            def onConnection(server, stream):
                print('someone connected!')

            server.add_listener('connection', onConnection)

            print(server.listeners('connection')) # [<function onConnection>]

        Arguments:
        - `event`: The event name
        """
        if not isinstance(getattr(self, "_events", None), dict) or \
           self._events.get(event) is None:
            return []
        if inspect.isfunction(self._events.get(event)):
            return [self._events[event]]
        return self._events[event][:]

    @staticmethod
    def listener_count(emitter, event):
        """Return the number of listeners for a given event.
        """
        if not isinstance(getattr(emitter, "_events", None), dict) or \
           emitter._events.get(event) is None:
            return 0
        if inspect.isfunction(emitter._events.get(event)):
            return 1
        return len(emitter._events[event])

EventEmitter.on = EventEmitter.add_listener
EventEmitter.default_max_listeners = 10
