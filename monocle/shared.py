from logging import getLogger, LoggerAdapter

from time import time
from asyncio import get_event_loop
from aiohttp import ClientSession

LOOP = get_event_loop()


class SessionManager:
    @classmethod
    def get(cls):
        try:
            return cls._session
        except AttributeError:
            cls._session = ClientSession(loop=LOOP)
            return cls._session

    @classmethod
    def close(cls):
        try:
            cls._session.close()
        except Exception:
            pass


class Message:
    def __init__(self, fmt, args):
        self.fmt = fmt
        self.args = args

    def __str__(self):
        return self.fmt.format(*self.args)


class StyleAdapter(LoggerAdapter):
    def __init__(self, logger, extra=None):
        super(StyleAdapter, self).__init__(logger, extra or {})

    def log(self, level, msg, *args, **kwargs):
        if self.isEnabledFor(level):
            msg, kwargs = self.process(msg, kwargs)
            self.logger._log(level, Message(msg, args), (), **kwargs)


def get_logger(name=None):
    return StyleAdapter(getLogger(name))


def call_later(delay, cb, *args):
    """Thread-safe wrapper for call_later"""
    try:
        return LOOP.call_soon_threadsafe(LOOP.call_later, delay, cb, *args)
    except RuntimeError:
        if not LOOP.is_closed():
            raise


def call_at(when, cb, *args):
    """Run call back at the unix time given"""
    delay = when - time()
    return call_later(delay, cb, *args)
