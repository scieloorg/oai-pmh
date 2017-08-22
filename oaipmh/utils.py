import datetime


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

