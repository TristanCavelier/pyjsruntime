# pyjsruntime

A python module to code as in javascript

## Getting Started

    from jsruntime import setScript, setTimeout, clearTimeout

    def main_script():
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

    setTimeout(main_script) # run main_script in another thread

## Use workers

    from jsruntime import setScript, setTimeout, clearTimeout
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

## API

- `setTimeout(function, timeout=0) -> ident`
- `clearTimeout(ident)`
- `setInterval(function, interval=0) -> ident`
- `clearInterval(ident)`
- `setImmediate(function, interval=0) -> ident`
- `clearImmediate(ident)`

## License

MIT License
