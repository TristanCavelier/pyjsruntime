# pyjsruntime

A python module to code as in javascript.

The goal is to use the power of the python language and libraries with the
javascript runtime. Each context have a queue of function to execute. Empty
contexts are deleted in order to let the memory free.

## Getting Started

To run the first context, you have to run setTimeout once.

    from jsruntime import setTimeout, clearTimeout

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

    setTimeout(main) # run main in another thread

## Use workers

Each workers have their own context.

    from jsruntime import setTimeout, clearTimeout
    from workers import Worker

    def task(emitter):
        def onMessage(emitter, message):
            print("Worker recv:", message)
            emitter.postMessage('Hello from worker!')
        emitter.on('message', onMessage)

    def main():
        def onMessage(w, message):
            print("Main recv:", message)
        w = Worker(task)
        w.on('message', onMessage)
        w.postMessage('Hello from main!')
        w.postMessage('Hello from main!')

    setTimeout(main)

## Use promises

You can create your own promises library like in javascript. See great promises
libraries like [Task.js](http://taskjs.org/), or
[RSVP.js](https://github.com/tildeio/rsvp.js).

## Provided functions

- `setTimeout(function, timeout=0) -> ident`
- `clearTimeout(ident)`
- `setInterval(function, interval=0) -> ident`
- `clearInterval(ident)`
- `setImmediate(function) -> None`

## License

MIT License
