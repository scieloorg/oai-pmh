from collections import namedtuple

from oaipmh import serializers, datastores


RepositoryMeta = namedtuple('RepositoryMeta', '''repositoryName baseURL
        protocolVersion adminEmail earliestDatestamp deletedRecord
        granularity''')


OAIRequest = namedtuple('OAIRequest', '''verb identifier metadataPrefix set
        resumptionToken from_ until''')


def asdict(namedtupl):
    """Produz uma instância de ``dict`` à partir da namedtuple ``namedtupl``.
    Underscores no início ou fim do nome do atributo serão removidos.
    """
    return {k.strip('_'):v for k, v in namedtupl._asdict().items()}


def identify(repo: RepositoryMeta, oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_identify(data)


def get_record(repo: RepositoryMeta, oai_request: OAIRequest,
        resource: datastores.Resource) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': [asdict(resource)],
            }

    return serializers.serialize_get_record(data)

