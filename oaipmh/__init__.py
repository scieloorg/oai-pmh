import os

from pyramid.config import Configurator
from pyramid.events import NewRequest

from oaipmh import (
        repository,
        datastores,
        sets,
        utils,
        articlemeta,
        entities,
        )
from oaipmh.formatters import (
        oai_dc,
        oai_dc_openaire,
        )


METADATA_FORMATS = [
        (entities.MetadataFormat(
            metadataPrefix='oai_dc',
            schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
         oai_dc.make_metadata,
         lambda x: x),
        (entities.MetadataFormat(
            metadataPrefix='oai_dc_openaire',
            schema='http://www.openarchives.org/OAI/2.0/oai_dc.xsd',
            metadataNamespace='http://www.openarchives.org/OAI/2.0/oai_dc/'),
         oai_dc_openaire.make_metadata,
         oai_dc_openaire.augment_metadata),
        ]


STATIC_SETS = [
        (sets.Set(setSpec='openaire', setName='OpenAIRE'),
         datastores.identityview),
        ]


DEFAULT_SETTINGS = [
        ('oaipmh.repo.name', 'OAIPMH_REPO_NAME', str,
            'SciELO - Scientific Electronic Library Online'),
        ('oaipmh.repo.baseurl', 'OAIPMH_REPO_BASEURL', str,
            'http://www.scielo.br/oai/scielo-oai.php'),
        ('oaipmh.repo.protocolversion', 'OAIPMH_REPO_PROTOCOLVERSION', str,
            '2.0'),
        ('oaipmh.repo.adminemail', 'OAIPMH_REPO_ADMINEMAIL', str,
            'scielo@scielo.org'),
        ('oaipmh.repo.earliestdatestamp', 'OAIPMH_REPO_EARLIESTDATESTAMP',
            utils.parse_date, '1998-08-01'),
        ('oaipmh.repo.deletedrecord', 'OAIPMH_REPO_DELETEDRECORD', str,
            'no'),
        ('oaipmh.repo.granularity', 'OAIPMH_REPO_GRANULARITY', str,
            'YYYY-MM-DD'),
        ('oaipmh.collection', 'OAIPMH_COLLECTION', str,
            'scl'),
        ('oaipmh.listslen', 'OAIPMH_LISTSLEN', int,
            20),
        ]


def parse_settings(settings):
    """Analisa e retorna as configurações da app com base no arquivo .ini e env.

    As variáveis de ambiente possuem precedência em relação aos valores
    definidos no arquivo .ini.
    """
    parsed = {}
    cfg = list(DEFAULT_SETTINGS)

    for name, envkey, convert, default in cfg:
        value = os.environ.get(envkey, settings.get(name, default))
        if convert is not None:
            value = convert(value)
        parsed[name] = value

    return parsed


def get_datastore(settings):
    client = articlemeta.get_articlemeta_client(settings['oaipmh.collection'])
    return articlemeta.ArticleMeta(client)


def get_repository_meta(settings):
    repometa = repository.RepositoryMeta(
            repositoryName=settings['oaipmh.repo.name'],
            baseURL=settings['oaipmh.repo.baseurl'],
            protocolVersion=settings['oaipmh.repo.protocolversion'],
            adminEmail=settings['oaipmh.repo.adminemail'],
            earliestDatestamp=settings['oaipmh.repo.earliestdatestamp'],
            deletedRecord=settings['oaipmh.repo.deletedrecord'],
            granularity=settings['oaipmh.repo.granularity'])
    return repometa


def add_oai_repository(event):
    settings = event.request.registry.settings
    ds = get_datastore(settings)

    event.request.repository = repository.Repository(
            settings['repository_meta'], ds, sets.SetsRegistry(ds, STATIC_SETS),
            settings['oaipmh.listslen'])

    for metadata, formatter, augmenter in METADATA_FORMATS:
        event.request.repository.add_metadataformat(metadata, formatter,
                augmenter)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=parse_settings(settings))

    config.registry.settings['repository_meta'] = get_repository_meta(
            config.registry.settings)

    config.add_subscriber(add_oai_repository, NewRequest)

    # URL patterns
    config.add_route('root', '/')

    config.scan()
    return config.make_wsgi_app()

