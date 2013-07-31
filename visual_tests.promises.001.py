# -*- coding: utf-8 -*-

from jsruntime import setTimeout
import promises
import time

if __name__ == '__main__':
    def main():
        def execute():
            d = promises.Deferred()
            d.resolve(12)
            return d.promise()
        def onDone(answer=None):
            print('done ' + str(answer))
        def onFail(answer=None):
            print('fail ' + str(answer))
        def nThen(answer=None):
            print('then ' + str(answer))
            if answer == 13:
                raise ValueError('13 is 13!')
            return answer + 1
        def errThen(answer=None):
            print('errthen ' + str(answer))
        p = execute()
        p.then(nThen, errThen).\
            then(nThen, errThen).\
            done(onDone).\
            fail(onFail)
        p.done(onDone).then(nThen, errThen)

    setTimeout(main)
