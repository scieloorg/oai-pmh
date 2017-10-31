import datetime
import calendar
import itertools


def parse_date(datestamp):
    fmts = ['%Y-%m-%d', '%Y-%m', '%Y']
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(datestamp, fmt)
        except ValueError:
            continue
    else:
        raise ValueError("time data '%s' does not match formats '%s'" % (
            datestamp, fmts))


class lazyproperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, cls):
        if instance is None:
            return self
        else:
            value = self.func(instance)
            setattr(instance, self.func.__name__, value)
            return value


def lastdayofmonth(year, month):
    """Retorna o último dia do mês em determinado ano.
    """
    try:
        days = list(calendar.Calendar().itermonthdays(int(year), int(month)))
    except calendar.IllegalMonthError:
        raise ValueError('illegal month: %s' % month)

    return next(itertools.dropwhile(lambda x: x == 0, reversed(days)))

