"""Serializadores baseados em pipelines de transformação.

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
import re
import logging
from datetime import datetime
from unicodedata import normalize

import plumber
from lxml import etree


LOGGER = logging.getLogger(__name__)


XMLNS = "http://www.openarchives.org/OAI/2.0/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMALOCATION = ' '.join(['http://www.openarchives.org/OAI/2.0/',
    'http://www.openarchives.org/OAI/2.0/OAI-PMH.xsd'])
ATTRIB = {"{%s}schemaLocation" % XSI: SCHEMALOCATION}


_punct_re = re.compile(r'[\t !"#$%&\'()*\-/<=>?@\[\\\]^_`{|},.]+')


def _slugify(text, delim='-'):
    """Generates an slightly worse ASCII-only slug.
    Originally from:
    http://flask.pocoo.org/snippets/5/
    Generating Slugs
    By Armin Ronacher filed in URLs
    """
    result = []
    for word in _punct_re.split(text.lower()):
        word = normalize('NFKD', word).encode('ascii', 'ignore')
        if word:
            result.append(word.decode('ascii'))
    return delim.join(result)


def deleted_precond(item):
    _, data = item
    if data.get('deleted'):
        raise plumber.UnmetPrecondition()


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
    return (xml, data)


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
        sub.attrib[key] = value
    sub.text = data['repository'].get('baseURL')
    return (xml, data)


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

    return (xml, data)


#----------------------
# Atende exclusivamente ao verbo ListMetadataFormats
#----------------------
@plumber.filter
def listmetadataformats(item):
    """Acrescenta o elemento ``/OAI-PMH/ListMetadataFormats`` e seus
    elementos-filhos.

    Essa função espera receber um dicionário de dados conforme o exemplo:

    .. code-block:: python

        data = {
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

    return (xml, data)


@plumber.filter
def listidentifiers(item):
    xml, data = item
    listidentifiers_elem = etree.SubElement(xml, 'ListIdentifiers')

    for resource in data.get('resources', []):
        header = etree.SubElement(listidentifiers_elem, 'header')
        if resource.get('deleted', False) is True:
            header.attrib['status'] = 'deleted'

        identifier = etree.SubElement(header, 'identifier')
        identifier.text = resource.get('ridentifier')

        datestamp = etree.SubElement(header, 'datestamp')
        datestamp.text = resource.get('datestamp').strftime('%Y-%m-%d')

        for _set in resource.get('setspec', []):
            setspec = etree.SubElement(header, 'setSpec')
            setspec.text = _set

    return (xml, data)


class SetPipe(plumber.Filter):
    def transform(self, data):
        sets = etree.Element('set')

        set_spec = etree.SubElement(sets, 'setSpec')
        set_spec.text = _slugify(data)

        set_name = etree.SubElement(sets, 'setName')
        set_name.text = data

        return sets


class ListSetsPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'ListSets')

        ppl = plumber.Pipeline(
            SetPipe()
        )
        sets = data.get('books')
        results = ppl.run(sets)

        for _set in results:
            sub.append(_set)

        return (xml, data)


class MetadataPipe(plumber.Filter):
    xmlns = "http://www.openarchives.org/OAI/2.0/oai_dc/"
    dc = "http://purl.org/dc/elements/1.1/"
    xsi = "http://www.w3.org/2001/XMLSchema-instance"
    schemaLocation = "http://www.openarchives.org/OAI/2.0/oai_dc/"
    schemaLocation += " http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
    attrib = {"{%s}schemaLocation" % xsi: schemaLocation}

    @plumber.precondition(deleted_precond)
    def transform(self, item):
        xml, data = item
        metadata = etree.SubElement(xml, 'metadata')
        oai_rec = etree.SubElement(metadata, '{%s}dc' % self.xmlns,
            nsmap={'oai_dc': self.xmlns, 'dc': self.dc, 'xsi': self.xsi},
            attrib=self.attrib
        )

        title = etree.SubElement(oai_rec, '{%s}title' % self.dc)
        title.text = data.get('title')

        creator = etree.SubElement(oai_rec, '{%s}creator' % self.dc)
        try:
            creator.text = data.get('creators').get('organizer')[0][0]
        except TypeError:
            oai_rec.remove(creator)
            logger.info("Can't get organizer for id %s" % data.get('identifier'))

        contributor = etree.SubElement(oai_rec, '{%s}contributor' % self.dc)
        try:
            contributor.text = data.get('creators').get('collaborator')[0][0]
        except TypeError:
            oai_rec.remove(contributor)
            logger.info("Can't get collaborator for id %s" % data.get('identifier'))

        description = etree.SubElement(oai_rec, '{%s}description' % self.dc)
        description.text = data.get('description')

        publisher = etree.SubElement(oai_rec, '{%s}publisher' % self.dc)
        publisher.text = data.get('publisher')

        date = etree.SubElement(oai_rec, '{%s}date' % self.dc)
        date.text = data.get('date')

        _type = etree.SubElement(oai_rec, '{%s}type' % self.dc)
        _type.text = 'book'

        for f in data.get('formats', []):
            format = etree.SubElement(oai_rec, '{%s}format' % self.dc)
            format.text = f

        identifier = etree.SubElement(oai_rec, '{%s}identifier' % self.dc)
        identifier.text = 'http://books.scielo.org/id/%s' % data.get('identifier')

        language = etree.SubElement(oai_rec, '{%s}language' % self.dc)
        language.text = data.get('language')

        return (xml, data)


class RecordPipe(plumber.Filter):
    def transform(self, data):
        record = etree.Element('record')

        ppl = plumber.Pipeline(
            header,
            MetadataPipe()
        )
        results = ppl.run([(record, data)])

        for result in results:
            pass

        return record


class GetRecordPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'GetRecord')

        ppl = plumber.Pipeline(
            RecordPipe(),
        )
        results = ppl.run(data.get('books'))
        record = next(results)
        sub.append(record)

        return (xml, data)


class ListRecordsPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'ListRecords')

        ppl = plumber.Pipeline(
            RecordPipe(),
        )
        results = ppl.run(data.get('books'))

        for record in results:
            sub.append(record)

        return (xml, data)


class BadVerbPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'badVerb'
        sub.text = 'Illegal OAI verb'
        return (xml, data)


class IdNotExistPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'idDoesNotExist'
        sub.text = 'No matching identifier'
        return (xml, data)


class NoRecordsPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'noRecordsMatch'
        return (xml, data)


class BadArgumentPipe(plumber.Filter):
    def transform(self, item):
        xml, data = item
        sub = etree.SubElement(xml, 'error')
        sub.attrib['code'] = 'badArgument'
        return (xml, data)


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

