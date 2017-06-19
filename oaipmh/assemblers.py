import plumber

from . import filters


IDENTIFY_PIPELINE = plumber.Pipeline(filters.root, filters.responsedate,
        filters.request, filters.identify, filters.tobytes)


def make_identify(request, repository):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            }

    output = next(IDENTIFY_PIPELINE.run(data, rewrap=True))
    return output

