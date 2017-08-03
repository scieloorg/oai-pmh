import os

from pyramid.config import Configurator
from pyramid.events import NewRequest

from oaipmh import (
        repository,
        datastores,
        )


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
            datastores.parse_date, '1998-08-01'),
        ('oaipmh.repo.deletedrecord', 'OAIPMH_REPO_DELETEDRECORD', str,
            'no'),
        ('oaipmh.repo.granularity', 'OAIPMH_REPO_GRANULARITY', str,
            'YYYY-MM-DD'),
        ('oaipmh.collection', 'OAIPMH_COLLECTION', str,
            'scl'),
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
    client = datastores.get_articlemeta_client(settings['oaipmh.collection'])
    return datastores.ArticleMeta(client)


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
    event.request.repository = repository.Repository(
            settings['repository_meta'], get_datastore(settings))


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

