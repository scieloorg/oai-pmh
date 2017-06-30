from lxml import etree


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


def make_metadata(resource):
    metadata = etree.Element('metadata')
    oai_rec = etree.SubElement(metadata, '{%s}dc' % OAIDC,
        nsmap={'oai_dc': OAIDC, 'dc': DC, 'xsi': XSI},
        attrib=ATTRIB
    )

    for maker in MAKERS_REGISTRY:
        for element in maker(resource):
            oai_rec.append(element)

    return metadata


def make_element_from_str(resource, name):
    elements = []
    for value in resource.get(name, []):
        elem = etree.Element('{%s}%s' % (DC, name))
        elem.text = value
        elements.append(elem)

    return elements


def make_element_from_pair(resource, name):
    elements = []
    for _, value in resource.get(name, []):
        elem = etree.Element('{%s}%s' % (DC, name))
        elem.text = value
        elements.append(elem)

    return elements


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
def make_publisher(resource):
    return make_element_from_str(resource, 'publisher')


@register_maker
def make_date(resource):
    return make_element_from_str(resource, 'date')


@register_maker
def make_type(resource):
    return make_element_from_str(resource, 'type')


@register_maker
def make_format(resource):
    return make_element_from_str(resource, 'format')


@register_maker
def make_identifier(resource):
    return make_element_from_str(resource, 'identifier')


@register_maker
def make_language(resource):
    return make_element_from_str(resource, 'language')

