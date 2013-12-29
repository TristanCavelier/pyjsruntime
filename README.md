# pyjsruntime

A python module to code as in javascript.

The goal is to use the power of the python language and libraries with the
javascript runtime. Each context have a queue of function to execute. Empty
contexts are deleted in order to let the memory free.

## Getting Started

To run the first context, you have to run setTimeout once.

    from jsruntime import run, setTimeout, clearTimeout

    def main():
        def two():
            print(2)

        def three():
            print(3)

        def four():
            print(4)

        setTimeout(two, 1)

        i = setTimeout(three, 1)
        clearTimeout(i)

        setTimeout(four, 2)

        print(1)

    run(main) # run main in another thread

## Use workers

Each workers have their own context.

    from jsruntime import run, on, postMessage, worker, setTimeout, clearTimeout

    def task():
        def on_message(message):
            print("Worker recv:", message)
            postMessage('Hello from worker!')
        on('message', on_message)

    def main():
        def on_message(message):
            print("Main recv:", message)
        w = worker(task)
        w.on('message', on_message)
        w.postMessage('Hello from main!')
        w.postMessage('Hello from main!')

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
- `postMessage(message)`

Timer management

- `setTimeout(function, [timeout, *args, **kwargs]) -> ident`
- `clearTimeout(ident)`
- `setInterval(function, [interval, *args, **kwargs]) -> ident`
- `clearInterval(ident)`
- `setImmediate(function, [*args, **kwargs])`

## License

GNU GPLv3
