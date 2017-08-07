"""Serializadores baseados em pipelines de transformação.


Todos os filtros operam sob a estrutura de dados descrita abaixo, ou em partes
dela no caso dos sub-pipelines.

    .. code-block:: python

        {
            'repository': {
                'repositoryName': <str>,
                'baseURL': <str>,
                'protocolVersion': <str>,
                'adminEmail': <str>,
                'earliestDatestamp': <datetime>,   
                'deletedRecord': <str>,
                'granularity': <str>,
            },
            'request': {
                'verb': <str>,
                'identifier': <str>,
                'metadataPrefix': <str>,
                'set': <str>,
                'resumptionToken': <str>,
                'from': <str>,
                'until': <str>,
            },
            'resources': [
                {
                    'ridentifier': <str>,
                    'datestamp': <str>,
                    'setspec': <List[str]>,
                    'title': <List[Tuple[str, str]]>,
                    'creator': <List[str]>,
                    'subject': <List[Tuple[str, str]]>,
                    'description': <List[Tuple[str, str]]>,
                    'publisher': <List[str]>,
                    'contributor': <List[str]>,
                    'date': <List[str]>,
                    'type': <List[str]>,
                    'format': <List[str]>,
                    'identifier': <List[str]>,
                    'source': <List[str]>,
                    'language': <List[str]>,
                    'relation': <List[str]>,
                    'rights': <List[str]>,
                },

            ],
            'formats': [
                {
                    'metadataPrefix': <str>,
                    'schema': <str>,
                    'metadataNamespace': <str>,
                },
            ],
            'sets': [
                {
                    'setSpec': <str>,
                    'setName': <str>,
                },
            ],
            'resumptionToken': <str>,
        }

"""
import logging
from datetime import datetime

import plumber
from lxml import etree

from .formatters import oai_dc
from . import validators


__all__ = ['serialize_identify', 'serialize_list_metadata_formats',
        'serialize_list_identifiers', 'serialize_list_records',
        'serialize_get_record']


LOGGER = logging.getLogger(__name__)


@validators.validate_on_debug
def serialize_identify(data):
    ppl = plumber.Pipeline(root, responsedate, request, identify, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


@validators.validate_on_debug
def serialize_list_metadata_formats(data):
    ppl = plumber.Pipeline(root, responsedate, request, listmetadataformats,
            tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


@validators.validate_on_debug
def serialize_list_identifiers(data):
    ppl = plumber.Pipeline(root, responsedate, request, listidentifiers,
            tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


@validators.validate_on_debug
def serialize_list_records(data):
    ppl = plumber.Pipeline(root, responsedate, request, listrecords, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


@validators.validate_on_debug
def serialize_get_record(data):
    ppl = plumber.Pipeline(root, responsedate, request, getrecord, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


@validators.validate_on_debug
def serialize_list_sets(data):
    ppl = plumber.Pipeline(root, responsedate, request, listsets, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


def serialize_bad_verb(data):
    ppl = plumber.Pipeline(root, responsedate, request, badverb, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


def serialize_bad_argument(data):
    ppl = plumber.Pipeline(root, responsedate, request, badargument, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


def serialize_id_does_not_exist(data):
    ppl = plumber.Pipeline(root, responsedate, request, iddoesnotexist, tobytes)
    output = next(ppl.run(data, rewrap=True))
    return output


#-----------------------------------------------------------------------------
# Filtros e funções que operam a serialização dos dados
#-----------------------------------------------------------------------------
XMLNS = "http://www.openarchives.org/OAI/2.0/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMALOCATION = ' '.join(['http://www.openarchives.org/OAI/2.0/',
    'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'])
ATTRIB = {"{%s}schemaLocation" % XSI: SCHEMALOCATION}


@plumber.filter
def root(data):
    """Recebe uma coleção de dados e retorna uma tupla onde o primeiro
    elemento é a raíz de uma etree, e o segundo a mesma coleção de dados
    recebida como argumento.

    Deve ser sempre o primeiro filtro do pipeline principal.
    """
    xml = etree.Element('OAI-PMH', nsmap={None: XMLNS, 'xsi': XSI},
            attrib=ATTRIB)
    return (xml, data)


@plumber.filter
def tobytes(item):
    """Recebe uma tupla (<etree>, <data>) e retorna o XML codificado em UTF-8.

    Deve ser sempre o último filtro do pipeline principal.
    """
    xml, _ = item
    return etree.tostring(xml, encoding="utf-8", method="xml",
            xml_declaration=True)


@plumber.filter
def responsedate(item):
    """Acrescenta o elemento ``/OAI-PMH/responseDate``.

    É um UTCdatetime indicando a data e hora que a resposta foi
    enviada. Deve ser expresso em UTC.

    Saiba mais em:
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#XMLResponse
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#Dates
    """
    xml, data = item
    sub = etree.SubElement(xml, 'responseDate')
    sub.text = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    return item


@plumber.filter
def request(item):
    """Acrescenta o elemento ``/OAI-PMH/request``.

    Indica a requisição que originou a resposta.

    Essa função espera receber um dicionário de dados conforme o exemplo:

    .. code-block:: python

        {
            'repository': {
                'baseURL': <str>,
            },
            'request': {
                'verb': <str>,
                'identifier': <str>,
                'metadataPrefix': <str>,
                'set': <str>,
                'resumptionToken': <str>,
                'from': <str>,
                'until': <str>,
            },
        }

    Saiba mais em:
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#XMLResponse
    """
    xml, data = item
    sub = etree.SubElement(xml, 'request')
    for key, value in data['request'].items():
        if value is not None:
            sub.attrib[key] = value
    sub.text = data['repository'].get('baseURL')
    return item


@plumber.filter
def identify(item):
    """Acrescenta o elemento ``/OAI-PMH/Identify`` e seus elementos-filhos.

    Essa função espera receber um dicionário de dados conforme o exemplo:

    .. code-block:: python

        {
            'repository': {
                'repositoryName': <str>,
                'baseURL': <str>,
                'protocolVersion': <str>,
                'adminEmail': <str>,
                'earliestDatestamp': <datetime>,
                'deletedRecord': <str>,
                'granularity': <str>,
            }
        }

    Saiba mais em:
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#Identify
    """
    xml, data = item
    elements = ['repositoryName', 'baseURL', 'protocolVersion', 'adminEmail',
            'earliestDatestamp', 'deletedRecord', 'granularity']

    node = etree.SubElement(xml, 'Identify')
    for element in elements:
        sub = etree.SubElement(node, element)
        if 'earliestDatestamp' == element:
            dt = data['repository'].get(element)
            if dt:
                sub.text = dt.strftime('%Y-%m-%d')
        else:
            sub.text = data['repository'].get(element)

    return item


@plumber.filter
def listmetadataformats(item):
    """Acrescenta o elemento ``/OAI-PMH/ListMetadataFormats`` e seus
    elementos-filhos.

    Essa função espera receber um dicionário de dados conforme o exemplo:

    .. code-block:: python

        {
            'formats': [
                {
                    'metadataPrefix': 'oai_dc',
                    'schema': 'http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
                    'metadataNamespace': 'http://www.openarchives.org/OAI/2.0/oai_dc/',
                },
            ]
        }

    Saiba mais em:
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#ListMetadataFormats
    """
    xml, data = item
    elements = ['metadataPrefix', 'schema', 'metadataNamespace']

    list_metadata_formats = etree.SubElement(xml, 'ListMetadataFormats')

    for _format in data['formats']:
        metadata_format = etree.SubElement(list_metadata_formats,
                'metadataFormat')
        for element in elements:
            new_elem = etree.SubElement(metadata_format, element)
            new_elem.text = _format[element]

    return item


@plumber.filter
def header(item):
    """Adiciona o elemento ``header`` contendo metadados do recurso no repo.

    Esse filtro é parte integrante de um *sub pipeline* que opera em uma
    sequência de *resources*. 

    Essa função espera receber um dicionário de dados conforme o exemplo:

    .. code-block:: python

        {
            'ridentifier': <str>,
            'datestamp': <datetime>,
            'setspec': <List[str]>,
            'deleted': <bool>,
        }

    Saiba mais em:
      - https://www.openarchives.org/OAI/2.0/openarchivesprotocol.htm#Record
    """
    xml, data = item

    header_element = etree.SubElement(xml, 'header')
    if data.get('deleted', False) is True:
        header_element.attrib['status'] = 'deleted'

    identifier = etree.SubElement(header_element, 'identifier')
    identifier.text = data.get('ridentifier')

    datestamp = etree.SubElement(header_element, 'datestamp')
    datestamp.text = data.get('datestamp').strftime('%Y-%m-%d')

    for _set in data.get('setspec', []):
        setspec = etree.SubElement(header_element, 'setSpec')
        setspec.text = _set

    return item


@plumber.filter
def listidentifiers(item):
    xml, data = item
    listidentifiers_elem = etree.SubElement(xml, 'ListIdentifiers')

    resources_data = ((listidentifiers_elem, resource)
                      for resource in data.get('resources', []))

    add_headers_ppl = plumber.Pipeline(header)
    for _ in add_headers_ppl.run(resources_data): pass

    return item


def make_set(set_data):
    _set = etree.Element('set')

    set_spec = etree.SubElement(_set, 'setSpec')
    set_spec.text = set_data.get('setSpec')

    set_name = etree.SubElement(_set, 'setName')
    set_name.text = set_data.get('setName')

    return _set


@plumber.filter
def listsets(item):
    xml, data = item
    sub = etree.SubElement(xml, 'ListSets')

    sets = (make_set(s) for s in data.get('sets', []))
    for _set in sets:
        sub.append(_set)

    return item


def make_record(record_data):
    record = etree.Element('record')

    ppl = plumber.Pipeline(
        header,
    )
    xmltree, _ = next(ppl.run((record, record_data), rewrap=True))
    xmltree.append(oai_dc.make_metadata(record_data))

    return xmltree


@plumber.filter
def getrecord(item):
    xml, data = item
    sub = etree.SubElement(xml, 'GetRecord')

    records = (make_record(resource)
               for resource in data.get('resources', []))
    for rec in records:
        sub.append(rec)

    return item


@plumber.filter
def listrecords(item):
    xml, data = item
    sub = etree.SubElement(xml, 'ListRecords')

    records = (make_record(resource)
               for resource in data.get('resources', []))
    for rec in records:
        sub.append(rec)

    return item


@plumber.filter
def badverb(item):
    xml, data = item
    sub = etree.SubElement(xml, 'error')
    sub.attrib['code'] = 'badVerb'
    sub.text = 'Illegal OAI verb'
    return item


@plumber.filter
def iddoesnotexist(item):
    xml, data = item
    sub = etree.SubElement(xml, 'error')
    sub.attrib['code'] = 'idDoesNotExist'
    sub.text = 'No matching identifier'
    return item


class NoRecordsPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'noRecordsMatch'
        return (xml, data)


@plumber.filter
def badargument(item):
    xml, data = item
    sub = etree.SubElement(xml, 'error')
    sub.attrib['code'] = 'badArgument'
    return item


class MetadataFormatErrorPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'cannotDisseminateFormat'
        return (xml, data)


class BadResumptionTokenPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'badResumptionToken'
        return (xml, data)

