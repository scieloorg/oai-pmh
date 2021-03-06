import os
import re

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
        ('oaipmh.repo.granularity_regex', 'OAIPMH_REPO_GRANULARITY_REGEX',
            re.compile, r'^(\d{4})-(\d{2})-(\d{2})$'),
        ('oaipmh.collection', 'OAIPMH_COLLECTION', str,
            'scl'),
        ('oaipmh.listslen', 'OAIPMH_LISTSLEN', int,
            100),
        ('oaipmh.chunkedresumptiontoken.chunksize',
            'OAIPMH_CHUNKEDRESUMPTIONTOKEN_CHUNKSIZE', int, 12),
        ('oaipmh.articlemeta_uri', 'OAIPMH_ARTICLEMETA_URI', str,
            'articlemeta.scielo.org:11621'),
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
    client = articlemeta.get_articlemeta_client(settings['oaipmh.collection'],
            domain=settings['oaipmh.articlemeta_uri'])
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


def get_granularity_validator(settings):
    def validate(date_time):
        return bool(settings['oaipmh.repo.granularity_regex'].fullmatch(
            date_time))
    return validate


def get_setsregistry(settings):
    registry = articlemeta.ArticleMetaSetsRegistry(
            datastore=get_datastore(settings))
    for metadata, view in STATIC_SETS:
        registry.add(metadata, view)
    return registry


def get_resultpage_factory(settings):
    return repository.ResultPageFactory(ds=get_datastore(settings),
            setsreg=get_setsregistry(settings),
            listslen=settings['oaipmh.listslen'],
            chunk_size=settings['oaipmh.chunkedresumptiontoken.chunksize'],
            granularity_validator=get_granularity_validator(settings),
            earliest_datestamp=settings['oaipmh.repo.earliestdatestamp'])


def add_oai_repository(event):
    settings = event.request.registry.settings

    event.request.repository = repository.Repository(
            get_repository_meta(settings), get_datastore(settings),
            get_granularity_validator(settings),
            resultpage_factory=get_resultpage_factory(settings))

    for metadata, formatter, augmenter in METADATA_FORMATS:
        event.request.repository.add_metadataformat(metadata, formatter,
                augmenter)


def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    settings.update(parse_settings(settings))
    config = Configurator(settings=settings)

    config.add_subscriber(add_oai_repository, NewRequest)

    # URL patterns
    config.add_route('root', '/')

    config.scan()
    return config.make_wsgi_app()

