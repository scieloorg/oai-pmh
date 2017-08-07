import functools
import operator
from typing import Iterable
from collections import namedtuple

from oaipmh import serializers, datastores


RepositoryMeta = namedtuple('RepositoryMeta', '''repositoryName baseURL
        protocolVersion adminEmail earliestDatestamp deletedRecord
        granularity''')


OAIRequest = namedtuple('OAIRequest', '''verb identifier metadataPrefix set
        resumptionToken from_ until''')


MetadataFormat = namedtuple('MetadataFormat', '''metadataPrefix schema
        metadataNamespace''')


def asdict(namedtupl):
    """Produz uma instância de ``dict`` à partir da namedtuple ``namedtupl``.
    Underscores no início ou fim do nome do atributo serão removidos.
    """
    return {k.strip('_'):v for k, v in namedtupl._asdict().items()}


def serialize_identify(repo: RepositoryMeta, oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_identify(data)


def serialize_get_record(repo: RepositoryMeta, oai_request: OAIRequest,
        resource: datastores.Resource) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': [asdict(resource)],
            }

    return serializers.serialize_get_record(data)


def serialize_list_records(repo: RepositoryMeta, oai_request: OAIRequest,
        resources: Iterable[datastores.Resource]) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': [asdict(resource) for resource in resources],
            }

    return serializers.serialize_list_records(data)


def serialize_list_identifiers(repo: RepositoryMeta, oai_request: OAIRequest,
        resources: Iterable[datastores.Resource]) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': [asdict(resource) for resource in resources],
            }

    return serializers.serialize_list_identifiers(data)


def serialize_list_metadata_formats(repo: RepositoryMeta, oai_request: OAIRequest,
        formats: Iterable[MetadataFormat]) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'formats': [asdict(fmt) for fmt in formats],
            }

    return serializers.serialize_list_metadata_formats(data)


def serialize_bad_verb(repo: RepositoryMeta, oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_bad_verb(data)


def serialize_bad_argument(repo: RepositoryMeta,
        oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_bad_argument(data)


def serialize_id_does_not_exist(repo: RepositoryMeta,
        oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_id_does_not_exist(data)


def serialize_cannot_disseminate_format(repo: RepositoryMeta,
        oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_cannot_disseminate_format(data)


class BadArgumentError(Exception):
    """Lançada quando a requisição contém argumentos inválidos para o verbo
    definido.
    """


class check_request_args:
    """Valida os argumentos da requisição de acordo com as regras de cada verbo.

    :param checking_func: função que receberá como argumento a sequência de
    nomes dos atributos recebidos na requisição. A função deve retornar um
    valor booleano referente à validade dos atributos.
    """
    def __init__(self, checking_func):
        self.checking_func = checking_func

    def __call__(self, f):
        def wrapper(*args):
            _, oaireq = args  # opera apenas em instâncias de Repository
            detected_args = [k for k, v in asdict(oaireq).items() if v]
            if self.checking_func(detected_args):
                return f(*args)
            else:
                raise BadArgumentError()
        return wrapper


def is_equal(expected_args, detected_args):
    return set(expected_args) == set(detected_args)


def check_incomplete_listings_args(detected_args):
    args = set(detected_args)
    if 'verb' not in args:
        return False

    if 'resumptionToken' in args:
        return not any((operator.contains(args, arg)
                        for arg in ['from', 'until', 'set', 'metadataPrefix']))
    else:
        return 'metadataPrefix' in args


class Repository:
    def __init__(self, metadata: RepositoryMeta, ds: datastores.DataStore):
        self.metadata = metadata
        self.ds = ds
        self.formats = ['oai_dc']
        self.verbs = {
                'Identify': self._identify,
                'GetRecord': self._get_record,
                'ListRecords': self._list_records,
                'ListIdentifiers': self._list_identifiers,
                }

    def handle_request(self, oairequest):
        if oairequest.metadataPrefix not in self.formats:
            return serialize_cannot_disseminate_format(self.metadata, oairequest)

        try:
            verb = self.verbs[oairequest.verb]
        except KeyError:
            return serialize_bad_verb(self.metadata, oairequest)

        try:
            return verb(oairequest)
        except BadArgumentError:
            return serialize_bad_argument(self.metadata, oairequest)
        except datastores.DoesNotExistError:
            return serialize_id_does_not_exist(self.metadata, oairequest)

    @check_request_args(functools.partial(is_equal, ['verb']))
    def _identify(self, oairequest):
        return serialize_identify(self.metadata, oairequest)

    @check_request_args(functools.partial(is_equal, 
        ['verb', 'metadataPrefix', 'identifier']))
    def _get_record(self, oairequest):
        resource = self.ds.get(oairequest.identifier)
        return serialize_get_record(self.metadata, oairequest, resource)

    @check_request_args(check_incomplete_listings_args)
    def _list_records(self, oairequest):
        resources = self.ds.list(_from=oairequest.from_, until=oairequest.until)
        return serialize_list_records(self.metadata, oairequest, resources)

    @check_request_args(check_incomplete_listings_args)
    def _list_identifiers(self, oairequest):
        resources = self.ds.list(_from=oairequest.from_, until=oairequest.until)
        return serialize_list_identifiers(self.metadata, oairequest, resources)

