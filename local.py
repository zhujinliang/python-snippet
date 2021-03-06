# -*- coding: utf-8 -*-

try:
    from greenlet import getcurrent as get_ident
except ImportError:
    from thread import get_ident


def release_local(local):
    '''
    Releases the contents of the local for the current context.

    Example::

        >>> loc = Local()
        >>> loc.test = 12
        >>> release_local(loc)
        >>> hasattr(loc, 'test')
        False
    '''
    local.__release_local__()


class Local(object):
    __slots__ = ('__storage__', '__ident_func__')

    def __init__(self):
        object.__setattr__(self, '__storage__', {})
        object.__setattr__(self, '__ident_func__', get_ident)

    def __iter__(self):
        return iter(self.__storage__.items())

    def __getattr__(self, name):
        try:
            return self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        ident = self.__ident_func__()
        storage = self.__storage__
        try:
            storage[ident][name] = value
        except KeyError:
            storage[ident] = {name: value}

    def __delattr__(self, name):
        try:
            del self.__storage__[self.__ident_func__()][name]
        except KeyError:
            raise AttributeError(name)

    def __release_local__(self):
        self.__storage__.pop(self.__ident_func__(), None)



if __name__ == '__main__':
    import time
    import random
    import threading

    local = Local()
    def set_local():
        local.test = random.randrange(100)
        print '%s >> %s \n' % (threading.current_thread(), local.test)
        time.sleep(3)
        print 'After sleep. %s >> %s' % (threading.current_thread(), local.test)

    t1 = threading.Thread(target=set_local, name='SetLocalThread')
    t2 = threading.Thread(target=set_local, name='SetLocalThread')
    t1.start()
    t2.start()
    set_local()
    t1.join()
    t2.join()
    print '%s ended.' % threading.current_thread().name
