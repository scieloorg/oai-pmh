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


class Repository:
    def __init__(self, metadata: RepositoryMeta, ds: datastores.DataStore):
        self.metadata = metadata
        self.ds = ds

    def identify(self):
        request = OAIRequest(verb='Identify', identifier=None,
                metadataPrefix=None, set=None, resumptionToken=None, from_=None,
                until=None)
        return serialize_identify(self.metadata, request)

    def get_record(self, identifier, metadata_prefix='oai_dc'):
        request = OAIRequest(verb='GetRecord', identifier=identifier,
                metadataPrefix=metadata_prefix, set=None, resumptionToken=None,
                from_=None, until=None)
        resource = self.ds.get(identifier)
        return serialize_get_record(self.metadata, request, resource)

    def list_records(self, metadata_prefix='oai_dc', _from=None, until=None,
            set=None, resumption_token=None):
        request = OAIRequest(verb='ListRecords', identifier=None,
                metadataPrefix=metadata_prefix, set=set,
                resumptionToken=resumption_token, from_=_from, until=until)
        resources = self.ds.list(_from=_from, until=until)
        return serialize_list_records(self.metadata, request, resources)

