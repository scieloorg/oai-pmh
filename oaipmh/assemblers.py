import io
import logging
import functools

import plumber
from lxml import etree

from . import filters, catalogs


LOGGER = logging.getLogger(__name__)


def get_identify_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate,
            filters.request, filters.identify, filters.tobytes)


def get_listmetadataformats_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate, filters.request,
            filters.listmetadataformats, filters.tobytes)


def get_listidentifiers_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate, filters.request,
            filters.listidentifiers, filters.tobytes)


def get_listrecords_pipeline():
    return plumber.Pipeline(filters.root, filters.responsedate, filters.request,
            filters.listrecords, filters.tobytes)


def get_validator():
    xmlschema_doc = etree.parse(catalogs.SCHEMAS['OAI-PMH.xsd'])
    return etree.XMLSchema(xmlschema_doc)


class OAIValidator:
    """Valida ``xml_bytes`` contra a XSD do OAI-PMH na versão 2.0.
    """
    def __init__(self, xml_bytes):
        self.xml_bytes = xml_bytes

    def xml_doc(self):
        return etree.parse(io.BytesIO(self.xml_bytes))

    def validate(self):
        validator = get_validator()
        return validator(self.xml_doc())

    def __str__(self):
        """A representação textual do validador é útil quando em conjunto
        com a emissão de mensagens de log, pois permite que a validação seja
        executada de maneira preguiçosa.
        """
        return self.validate()


def validate_on_debug(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        res = f(*args, **kwargs)
        try:
            LOGGER.debug('the validatation status for "%s" is: %s', res,
                    OAIValidator(res))
        except Exception as exc:
            LOGGER.exception(exc)
        return res
    return wrapper


@validate_on_debug
def make_identify(request, repository):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            }

    ppl = get_identify_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output


@validate_on_debug
def make_list_metadata_formats(request, repository, formats):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            'formats': list(formats),
            }

    ppl = get_listmetadataformats_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output


@validate_on_debug
def make_list_identifiers(request, repository, resources):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            'resources': list(resources),
            }

    ppl = get_listidentifiers_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output


@validate_on_debug
def make_list_records(request, repository, resources):
    data = {
            'request': dict(request),
            'repository': dict(repository),
            'resources': list(resources),
            }

    ppl = get_listrecords_pipeline()
    output = next(ppl.run(data, rewrap=True))
    return output

