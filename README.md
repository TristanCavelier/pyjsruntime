# pyjsruntime

A python module to code as in javascript

## Getting Started

    from jsruntime import setScript, setTimeout, clearTimeout, quit

    def main_script():
        def two():
            print(2)

        def three():
            print(3)

        def four():
            print(4)
            quit() # terminate this script after the current callback

        setTimeout(two, 1)

        i = setTimeout(three, 1)
        clearTimeout(i)

        setTimeout(four, 2)

        print(1)

    setScript('MainScript', main_script) # run main_script in another thread

## API

- `setScript(script name, function)`
- `quit()`
- `setTimeout(function, timeout=0) -> ident`
- `clearTimeout(ident)`
- `setInterval(function, interval=0) -> ident`
- `clearInterval(ident)`
- `setImmediate(function, interval=0) -> ident`
- `clearImmediate(ident)`

## License

MIT License
