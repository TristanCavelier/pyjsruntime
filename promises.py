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
        self._answers = None
        self._kwanswers = None

    def solver(self, callback=None):
        if self._state == "running":
            raise EnvironmentError("Promise().execute(): Already running")
        elif self._state == "resolved":
            raise EnvironmentError("Promise().execute(): Resolved");
        elif self._state == "rejected":
            raise EnvironmentError("Promise().execute(): Rejected");
        def createSolver(promise):
            def resolve(*args, **kw):
                if promise._state != "resolved" and \
                   promise._state != "rejected":
                    promise._state = "resolved"
                    promise._answers = args
                    promise._kwanswers = kw
                    _forEach(
                        promise._onResolve,
                        lambda callback, i: \
                        setTimeout(lambda: callback(
                            *promise._answers,
                            **promise._kwanswers
                        ))
                    )
                    promise._onResolve = []
                    promise._onReject = []
                    promise._onProgress = []
            def reject(*args, **kw):
                if promise._state != "resolved" and \
                   promise._state != "rejected":
                    promise._state = "reject"
                    promise._answers = args
                    promise._kwanswers = kw
                    _forEach(
                        promise._onReject,
                        lambda callback, i: \
                        setTimeout(lambda: callback(
                            *promise._answers,
                            **promise._kwanswers
                        ))
                    )
                    promise._onResolve = []
                    promise._onReject = []
                    promise._onProgress = []
            def notify(*args, **kw):
                _forEach(
                    promise._onProgress,
                    lambda callback, i: \
                    setTimeout(lambda: callback(*args, **kw))
                )
            return Solver(resolve, reject, notify)
        self._state = "running"
        if str(type(callback)) == "<class 'function'>":
            setTimeout(lambda: callback(createSolver(self)))
            return self
        return createSolver(self)

    def then(self, onSuccess=None, onError=None, onProgress=None):
        necst = Promise()
        if self._state == "resolved":
            if str(type(onSuccess)) == "<class 'function'>":
                def wrapper(resolver):
                    try:
                        resolver.resolve(onSuccess(
                            *self._answers,
                            **self._kwanswers
                        ))
                    except Exception as e: resolver.reject(e)
                necst.solver(wrapper)
        elif self._state == "rejeted":
            if str(type(onError)) == "<class 'function'>":
                def wrapper(resolver):
                    try:
                        resolver.resolve(onError(
                            *self._answers,
                            **self._kwanswers
                        ))
                    except Exception as e: resolver.reject(e)
                necst.solver(wrapper)
        else:
            if str(type(onSuccess)) == "<class 'function'>":
                def onResolve(*args, **kw):
                    def wrapper(resolver):
                        try: resolver.resolve(onSuccess(*args, **kw))
                        except Exception as e: resolver.reject(e)
                    necst.solver(wrapper)
                self._onResolve.append(onResolve)
            if str(type(onError)) == "<class 'function'>":
                def onReject(*args, **kw):
                    def wrapper(resolver):
                        try: resolver.resolve(onError(*args, **kw))
                        except Exception as e: resolver.reject(e)
                    necst.solver(wrapper)
                self._onReject.append(onReject)
            if str(type(onProgress)) == "<class 'function'>":
                self._onProgress.append(onProgress)
        return necst

    def done(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state == "resolved":
            def wrapper():
                callback(*self._answers, **self._kwanswers)
            setTimeout(wrapper)
        else:
            self._onResolve.append(callback);
        return self

    def fail(self, callback):
        if str(type(callback)) != "<class 'function'>":
            return self
        if self._state == "rejected":
            def wrapper():
                callback(*self._answers, **self._kwanswers)
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
            setTimeout(lambda: callback(*self._answers, **self._kwanswers))
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
