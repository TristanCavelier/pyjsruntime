from jsruntime import setTimeout

class Solver(object):
    def __init__(self, resolve, reject, notify):
        self.resolve = resolve
        self.reject = reject
        self.notify = notify

def _forEach(array, callback):
    i = 0
    for v in array:
        callback(v, i)
        i += 1

class Promise(object):

    def __init__(self):
        self._onReject = []
        self._onResolve = []
        self._onProgress = []
        self._state = ""
        self._answer = None

    @staticmethod
    def createSolver(promise):
        def resolve(answer=None):
            if promise._state != "resolved" and promise._state != "rejected":
                promise._state = "resolved"
                promise._answer = answer
                def each(callback, i):
                    def wrapper():
                        callback(answer)
                    setTimeout(wrapper)
                _forEach(promise._onResolve, each)
                promise._onResolve = []
                promise._onReject = []
                promise._onProgress = []
        def reject(answer=None):
            if promise._state != "resolved" and promise._state != "rejected":
                promise._state = "rejected"
                promise._answer = answer
                def each(callback, i):
                    def wrapper():
                        callback(answer)
                    setTimeout(wrapper)
                _forEach(promise._onReject, each)
                promise._onResolve = []
                promise._onReject = []
                promise._onProgress = []
        def notify(answer=None):
            def each(callback, i):
                def wrapper():
                    callback(answer)
                setTimeout(wrapper)
            _forEach(promise._onProgress, each)

        solver = Solver(resolve, reject, notify)
        return solver

    def solver(self):
        if self._state == "running":
            raise EnvironmentError("Promise().execute(): Already running")
        elif self._state == "resolved":
            raise EnvironmentError("Promise().execute(): Resolved");
        elif self._state == "rejected":
            raise EnvironmentError("Promise().execute(): Rejected");
        self._state = "running"
        return Promise.createSolver(self);

    def execute(self, callback):
        if self._state == "running":
            raise EnvironmentError("Promise().execute(): Already running")
        elif self._state == "resolved":
            raise EnvironmentError("Promise().execute(): Resolved");
        elif self._state == "rejected":
            raise EnvironmentError("Promise().execute(): Rejected");
        self._state = "running"
        def wrapper():
            callback(Promise.createSolver(self))
        setTimeout(wrapper)
        return self

    def then(self, onSuccess=None, onError=None, onProgress=None):
        necst = Promise()
        if self._state == "resolved":
            if str(type(onSuccess)) == "<class 'function'>":
                def wrapper(resolver):
                    try: resolver.resolve(onSuccess(self._answer))
                    except Exception as e: resolver.reject(e)
                necst.execute(wrapper)
        elif self._state == "rejeted":
            if str(type(onError)) == "<class 'function'>":
                def wrapper(resolver):
                    try: resolver.resolve(onError(self._answer))
                    except Exception as e: resolver.reject(e)
                necst.execute(wrapper)
        else:
            if str(type(onSuccess)) == "<class 'function'>":
                def onResolve(answer=None):
                    def wrapper(resolver):
                        try: resolver.resolve(onSuccess(answer))
                        except Exception as e: resolver.reject(e)
                    necst.execute(wrapper)
                self._onResolve.append(onResolve)
            if str(type(onError)) == "<class 'function'>":
                def onReject(answer=None):
                    def wrapper(resolver):
                        try: resolver.resolve(onError(answer))
                        except Exception as e: resolver.reject(e)
                    necst.execute(wrapper)
                self._onReject.append(onReject)
            if str(type(onProgress)) == "<class 'function'>":
                self._onProgress.append(onProgress)
        return necst

    def done(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state == "resolved":
            def wrapper():
                callback(self._answer)
            setTimeout(wrapper)
        else:
            self._onResolve.append(callback);
        return self

    def fail(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state == "rejected":
            def wrapper():
                callback(self._answer)
            setTimeout(wrapper)
        else:
            self._onReject.append(callback)
        return self

    def progress(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state != "rejected" and self._state != "resolved":
            self._onProgress.append(callback)
        return self

    def always(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state == "rejected" or self._state == "resolved":
            def wrapper():
                callback(self._answer)
            setTimeout(wrapper)
        else:
            self._onReject.append(callback)
            self._onResolve.append(callback)
        return self


class Deferred(object):
    def __init__(self):
        self._promise = Promise()
        self._solver = self._promise.solver()

    def resolve(self, *args, **kwargs):
        self._solver.resolve(*args, **kwargs)

    def reject(self, *args, **kwargs):
        self._solver.reject(*args, **kwargs)

    def notify(self, *args, **kwargs):
        self._solver.notify(*args, **kwargs)

    def promise(self):
        return self._promise
