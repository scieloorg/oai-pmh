import plumber

from . import filters


def get_identify_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate,
            filters.request, filters.identify, filters.tobytes)


def get_listmetadataformats_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate, filters.request,
            filters.listmetadataformats, filters.tobytes)


def get_listidentifiers_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate, filters.request,
            filters.listidentifiers, filters.tobytes)


def make_identify(request, repository):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            }

    ppl = get_identify_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output


def make_list_metadata_formats(request, repository, formats):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            'formats': list(formats),
            }

    ppl = get_listmetadataformats_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output


def make_list_identifiers(request, repository, resources):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            'resources': list(resources),
            }

    ppl = get_listidentifiers_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output

