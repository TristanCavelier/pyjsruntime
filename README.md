# pyjsruntime

A python module to code as in javascript.

*Version 0.1.0*

The goal is to use the power of the python language and libraries with the
javascript runtime. Each context have a queue of function to execute. Empty
contexts are deleted in order to let the memory free.

## Getting Started

To run the first context, you have to run setTimeout once.

    from jsruntime import run, set_timeout, clear_timeout

    def main():
        def two():
            print(2)

        def three():
            print(3)

        def four():
            print(4)

        set_timeout(two, 1)

        i = set_timeout(three, 1)
        clear_timeout(i)

        set_timeout(four, 2)

        print(1)

    run(main) # run main in another thread

## Use workers

Each workers have their own context.

    from jsruntime import run, on, post_message, worker, set_timeout, clear_timeout

    def task():
        def on_message(message):
            print("Worker recv:", message)
            post_message('Hello from worker!')
        on('message', on_message)

    def main():
        def on_message(message):
            print("Main recv:", message)
        w = worker(task)
        w.on('message', on_message)
        w.post_message('Hello from main!')
        w.post_message('Hello from main!')

    run(main)

## Use promises

You can create your own promises library like in javascript. See great promises
libraries like [Task.js](http://taskjs.org/), or
[RSVP.js](https://github.com/tildeio/rsvp.js).

## Provided functions

First run

- `run(function, [*args, **kwargs])`

Event management

- `on(event_name, listener) = add_listener(event_name, listener)`
- `remove_listener(event_name, listener)`
- `post_message(message)`

Timer management

- `set_timeout(function, [timeout, *args, **kwargs]) -> ident`
- `clear_timeout(ident)`
- `set_interval(function, [interval, *args, **kwargs]) -> ident`
- `clear_interval(ident)`

## License

> Copyright (c) 2014 Tristan Cavelier <t.cavelier@free.fr>
> This program is free software. It comes without any warranty, to
> the extent permitted by applicable law. You can redistribute it
> and/or modify it under the terms of the Do What The Fuck You Want
> To Public License, Version 2, as published by Sam Hocevar. See
> the COPYING file for more details.
