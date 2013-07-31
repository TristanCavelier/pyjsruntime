# pyjsruntime

A python module to code as in javascript

## Getting Started

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

    from jsruntime import setTimeout, setInterval, clearInterval
    from workers import Worker
    from promises import Deferred

    """Show dots every second. A worker waits for something typed and resolve
    the promise with it. The typed message is shown and dots stop.
    """

    def promised_input():
        deferred = Deferred()
        def task(emitter):
            emitter.postMessage(input())
        def onMessage(emitter, message):
            deferred.resolve(message)
        w = Worker(task)
        w.on('message', onMessage)
        return deferred.promise()

    def main():
        def show_input_and_stop_dots(message):
            print(message)
            clearInterval(i)
        def show_activity():
            print('.')
        promised_input().then(show_input_and_stop_dots)
        i = setInterval(show_activity, 1)
    setTimeout(main)

## API

- `setTimeout(function, timeout=0) -> ident`
- `clearTimeout(ident)`
- `setInterval(function, interval=0) -> ident`
- `clearInterval(ident)`
- `setImmediate(function, interval=0) -> ident`
- `clearImmediate(ident)`

## License

MIT License
