from lxml import etree

from oaipmh import entities


__all__ = ['make_metadata']


OAIDC = "http://www.openarchives.org/OAI/2.0/oai_dc/"
DC = "http://purl.org/dc/elements/1.1/"
XSI = "http://www.w3.org/2001/XMLSchema-instance"
SCHEMALOCATION = "http://www.openarchives.org/OAI/2.0/oai_dc/"
SCHEMALOCATION += " http://www.openarchives.org/OAI/2.0/oai_dc.xsd"
ATTRIB = {"{%s}schemaLocation" % XSI: SCHEMALOCATION}


MAKERS_REGISTRY = []


def register_maker(f):
    MAKERS_REGISTRY.append(f)
    return f


def make_metadata(resource: entities.Resource):
    metadata = etree.Element('metadata')
    oai_rec = etree.SubElement(metadata, '{%s}dc' % OAIDC,
        nsmap={'oai_dc': OAIDC, 'dc': DC, 'xsi': XSI},
        attrib=ATTRIB
    )

    for maker in MAKERS_REGISTRY:
        for element in maker(resource):
            oai_rec.append(element)

    return metadata


def augment_metadata(resource: entities.Resource):
    resource.rights.append('info:eu-repo/semantics/openAccess')
    resource.type[:] = [fetch_pubtype_from_vocabulary(t) for t in resource.type]
    return resource


ARTICLETYPE_TO_VOCABULARY_MAP = {
        'research-article': 'info:eu-repo/semantics/article',
        'article-commentary': 'info:eu-repo/semantics/other',
        'book-review': 'info:eu-repo/semantics/review',
        'brief-report': 'info:eu-repo/semantics/report',
        'case-report': 'info:eu-repo/semantics/report',
        'correction': 'info:eu-repo/semantics/other',
        'editorial': 'info:eu-repo/semantics/other',
        'in-brief': 'info:eu-repo/semantics/other',
        'letter': 'info:eu-repo/semantics/other',
        'other': 'info:eu-repo/semantics/other',
        'partial-retraction': 'info:eu-repo/semantics/other',
        'rapid-communication': 'info:eu-repo/semantics/other',
        'reply': 'info:eu-repo/semantics/other',
        'retraction': 'info:eu-repo/semantics/other',
        'review-article': 'info:eu-repo/semantics/article',
        }
def fetch_pubtype_from_vocabulary(typ):
    return ARTICLETYPE_TO_VOCABULARY_MAP.get(typ, 'info:eu-repo/semantics/other')


def make_element_from_str(resource, name, tostr=str):
    elements = []
    for value in resource.get(name, []):
        if value is None:
            continue
        elem = etree.Element('{%s}%s' % (DC, name))
        elem.text = tostr(value)
        elements.append(elem)

    return elements


def make_element_from_pair(resource, name):
    elements = []
    for _, value in resource.get(name, []):
        elem = etree.Element('{%s}%s' % (DC, name))
        elem.text = value
        elements.append(elem)

    return elements


# -- ATENÇÃO:
# A ordem de definição das funções decoradas por ``register_maker`` é
# a mesma em que os elementos serão ordenados no XML.
@register_maker
def make_title(resource):
    return make_element_from_pair(resource, 'title')

  
@register_maker
def make_creator(resource):
    return make_element_from_str(resource, 'creator')


@register_maker
def make_contributor(resource):
    return make_element_from_str(resource, 'contributor')


@register_maker
def make_description(resource):
    return make_element_from_pair(resource, 'description')


@register_maker
def make_subject(resource):
    return make_element_from_pair(resource, 'subject')


@register_maker
def make_publisher(resource):
    return make_element_from_str(resource, 'publisher')


@register_maker
def make_date(resource):
    def format_date(date):
        return date.strftime('%Y-%m-%d')
    return make_element_from_str(resource, 'date', tostr=format_date)


@register_maker
def make_type(resource):
    return make_element_from_str(resource, 'type')


@register_maker
def make_source(resource):
    return make_element_from_str(resource, 'source')


@register_maker
def make_format(resource):
    return make_element_from_str(resource, 'format')


@register_maker
def make_identifier(resource):
    return make_element_from_str(resource, 'identifier')


@register_maker
def make_rights(resource):
    return make_element_from_str(resource, 'rights')


@register_maker
def make_language(resource):
    return make_element_from_str(resource, 'language')

