#! -*- coding: UTF-8 -*-
# Copyright (c) 2012, Michał "teddy_beer_maniac" Przybyś
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions, the following disclaimer and the contact information.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions, the following disclaimer and the contact information
#    in the documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# email: miprzybys@gmail.com
# other: https://gravatar.com/teddybeermaniac
import threading

class AsyncMethodError(Exception):
    pass

class AlreadyRunningError(AsyncMethodError, RuntimeError):
    pass

class TimedOutError(AsyncMethodError, RuntimeError):
    pass

class AsyncResult:
    def __init__(self):
        self._event = threading.Event()
        self._exception = None
        self._result = None

    def __call__(self, timeout = None):
        if not self._event.wait(timeout):
            raise TimedOutError
        elif self._exception is not None:
            raise self._exception
        else:
            return self._result

    def _raise(self, exception):
        self._exception = exception
        self._event.set()

    def _return(self, result):
        self._result = result
        self._event.set()


class AsyncMethod:
    def __init__(self, function):
        self._function = function
        self._running = threading.Lock()

    def __call__(self, *args, **kwargs):
        return self._start(args, kwargs)

    def _start(self, args, kwargs):
        if not self._running.acquire():
            raise AlreadyRunningError

        callback_error = None
        if ('callback_error' in kwargs and callable(kwargs['callback_error'])):
            callback_error = kwargs.pop('callback_error')
            
        callback_success = None
        if ('callback_success' in kwargs and callable(kwargs['callback_success'])):
            kwargs.pop('callback_success')

        result = AsyncResult()
        threading.Thread(target = self._wrapper, args = (self._function, args, kwargs, result, callback_error, callback_success)).start()

        return result

    def _wrapper(self, function, args, kwargs, result, callback_error, callback_success):
        try:
            value = function(*args, **kwargs)
        except Exception, exception:
            result._raise(exception)
            if callback_error is not None:
                try:
                    callback_error(exception)
                except:
                    pass
        else:
            result._return(value)
            if callback_success is not None:
                try:
                    callback_success(value)
                except:
                    pass
        self._running.release()


def asyncmethod(function):
    def asyncmethod(*args, **kwargs):
        return AsyncMethod(function)._start(args, kwargs)

    return asyncmethod

def asynconcemethod(function):
    async = AsyncMethod(function)
    def asynconcemethod(*args, **kwargs):
        return async._start(args, kwargs)

    return asynconcemethod

__all__ = ['AlreadyRunningError', 'AsyncMethodError', 'TimedOutError', 'asyncmethod', 'asynconcemethod']