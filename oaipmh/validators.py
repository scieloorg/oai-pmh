import io
import logging
import functools

from lxml import etree

from . import catalogs


LOGGER = logging.getLogger(__name__)


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
        return (validator(self.xml_doc()), validator.error_log)

    def __str__(self):
        """A representação textual do validador é útil quando em conjunto
        com a emissão de mensagens de log, pois permite que a validação seja
        executada de maneira preguiçosa.
        """
        return str(self.validate())


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

