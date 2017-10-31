import functools
import itertools
import operator
import logging
from typing import (
        Iterable,
        Callable,
        )
import urllib.parse
from datetime import datetime

from .formatters import oai_dc
from . import (
        serializers,
        datastores,
        sets,
        exceptions,
        utils,
        )
from .entities import (
        RepositoryMeta,
        OAIRequest,
        MetadataFormat,
        ResumptionToken,
        ChunkedResumptionToken,
        PlainResumptionToken,
        )


LOGGER = logging.getLogger(__name__)


OAIPMH_LEGAL_ARGS = set(['verb', 'identifier', 'metadataPrefix', 'set',
            'resumptionToken', 'from', 'until'])


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
        resource: datastores.Resource, *, metadata_formatter) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': [asdict(resource)],
            }

    return serializers.serialize_get_record(data, metadata_formatter)


def serialize_list_records(repo: RepositoryMeta, oai_request: OAIRequest,
        resources: Iterable[datastores.Resource],
        resumption_token: ResumptionToken, *, metadata_formatter) -> bytes:

    if resumption_token is None:
        encoded_resumption_token = ''
    else:
        encoded_resumption_token = resumption_token.encode()

    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': (asdict(resource) for resource in resources),
            'resumptionToken': encoded_resumption_token,
            }
    return serializers.serialize_list_records(data, metadata_formatter)


def serialize_list_identifiers(repo: RepositoryMeta, oai_request: OAIRequest,
        resources: Iterable[datastores.Resource],
        resumption_token: ResumptionToken) -> bytes:

    if resumption_token is None:
        encoded_resumption_token = ''
    else:
        encoded_resumption_token = resumption_token.encode()

    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'resources': (asdict(resource) for resource in resources),
            'resumptionToken': encoded_resumption_token,
            }

    return serializers.serialize_list_identifiers(data)


def serialize_list_metadata_formats(repo: RepositoryMeta, oai_request: OAIRequest,
        formats: Iterable[MetadataFormat]) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'formats': (asdict(fmt) for fmt in formats),
            }

    return serializers.serialize_list_metadata_formats(data)


def serialize_list_sets(repo: RepositoryMeta, oai_request: OAIRequest,
        sets: Iterable[sets.Set],
        resumption_token: ResumptionToken,) -> bytes:

    if resumption_token is None:
        encoded_resumption_token = ''
    else:
        encoded_resumption_token = resumption_token.encode()

    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            'sets': (asdict(s) for s in sets),
            'resumptionToken': encoded_resumption_token,
            }
    return serializers.serialize_list_sets(data)


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


def serialize_bad_resumption_token(repo: RepositoryMeta,
        oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_bad_resumption_token(data)


def serialize_no_records_match(repo: RepositoryMeta,
        oai_request: OAIRequest) -> bytes:
    data = {
            'repository': asdict(repo),
            'request': asdict(oai_request),
            }

    return serializers.serialize_no_records_match(data)


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
            _, oaireq = args
            detected_args = [k for k, v in asdict(oaireq).items() if v]
            if self.checking_func(detected_args):
                return f(*args)
            else:
                raise exceptions.BadArgumentError()
        return wrapper


def are_equal(expected_args, detected_args):
    return sorted(expected_args) == sorted(detected_args)


def check_listrecords_args(detected_args):
    args = set(detected_args)
    if 'verb' not in args:
        return False

    if 'resumptionToken' in args:
        return not any((operator.contains(args, arg)
                        for arg in ['from', 'until', 'set', 'metadataPrefix']))
    else:
        return 'metadataPrefix' in args


def check_listsets_args(detected_args):
    args = set(detected_args)
    if 'verb' not in args:
        return False

    if 'resumptionToken' in args:
        return not any((operator.contains(args, arg)
                        for arg in ['from', 'until', 'set']))
    else:
        return 'metadataPrefix' not in args


def check_listmetadataformats_args(detected_args):
    args = set(detected_args)
    if 'verb' not in args:
        return False

    return not any((operator.contains(args, arg)
                        for arg in ['from', 'until', 'set', 'metadataPrefix']))


def get_or_default(mapping, key, default=None):
    """Retorna o valor do índice 0 de ``mapping[key]`` ou ``default``.
    """
    try:
        values = mapping[key]
    except KeyError:
        return default
    return values[0]


def has_illegal_args(parsed_qstr, legal_args=OAIPMH_LEGAL_ARGS):
    for arg in parsed_qstr.keys():
        if arg not in legal_args:
            return True
    return False


def has_repeated_args(parsed_qstr):
    for value in parsed_qstr.values():
        if len(value) > 1:
            return True
    return False


def oairequest_from_querystring(parsed_qstr):
    return OAIRequest(
            verb=get_or_default(parsed_qstr, 'verb'),
            identifier=get_or_default(parsed_qstr, 'identifier'),
            metadataPrefix=get_or_default(parsed_qstr, 'metadataPrefix'),
            set=get_or_default(parsed_qstr, 'set'),
            resumptionToken=get_or_default(parsed_qstr, 'resumptionToken'),
            from_=get_or_default(parsed_qstr, 'from'),
            until=get_or_default(parsed_qstr, 'until'),
            )


def is_empty_resultset(resultset: Iterable) -> bool:
    """Testa de ``resultset`` está vazio.

    Atenção ao passar iteradores para essa função; nesse caso é recomendado
    espelhar o iterador antes por meio da função ``itertools.tee``.
    """
    for _ in resultset:
        return False
    return True


class Repository:
    def __init__(self, metadata: RepositoryMeta, ds: datastores.DataStore,
            granularity_validator: Callable, resultpage_factory=None):
        self.metadata = metadata
        self.ds = ds
        self.granularity_validator = granularity_validator
        self.formats = {}
        self.verbs = {
                'Identify': self.identify,
                'GetRecord': self.get_record,
                'ListRecords': self.list_records,
                'ListIdentifiers': self.list_identifiers,
                'ListMetadataFormats': self.list_metadata_formats,
                'ListSets': self.list_sets,
                }
        self._resultpage = resultpage_factory

    def add_metadataformat(self, metadata: MetadataFormat, formatter, augmenter):
        """Registra formatos de metadados suportados pelo repositório.

        :param metadata: descreve o formato.
        :param formatter: função que dado um dicionário, produz uma árvore de 
        elementos XML (etree.Element).
        :param augmenter: função que dado um dicionário, produz outro dicionário.
        Este último será o argumento para a função ``formatter``.
        """
        self.formats[metadata.metadataPrefix] = {
                'metadata': metadata,
                'formatter': formatter,
                'augmenter': augmenter,
                }

    def handle_request(self, qstr: str):
        """Trata a requisição ``qstr`` codificada como querystring.
        """
        parsed_qstr = urllib.parse.parse_qs(qstr)
        oairequest = oairequest_from_querystring(parsed_qstr)

        LOGGER.info('handling OAI request: %s', repr(oairequest))

        if has_illegal_args(parsed_qstr) or has_repeated_args(parsed_qstr):
            return serialize_bad_argument(self.metadata,
                    self._clean_oairequest(oairequest))

        try:
            verb = self.verbs[oairequest.verb]
        except KeyError:
            return serialize_bad_verb(self.metadata,
                    self._clean_oairequest(oairequest))

        try:
            return verb(oairequest)
        except exceptions.BadArgumentError:
            return serialize_bad_argument(self.metadata,
                    self._clean_oairequest(oairequest))
        except exceptions.IdDoesNotExistError:
            return serialize_id_does_not_exist(self.metadata, oairequest)
        except exceptions.BadResumptionTokenError:
            return serialize_bad_resumption_token(self.metadata, oairequest)
        except exceptions.NoRecordsMatchError:
            return serialize_no_records_match(self.metadata, oairequest)
        except exceptions.CannotDisseminateFormatError:
            return serialize_cannot_disseminate_format(self.metadata,
                    oairequest)

    def _clean_oairequest(self, oairequest: OAIRequest):
        """Remove valores inválidos de oairequest.
        """
        return clean_oairequest_dates(clean_oairequest_verb(oairequest),
                self.granularity_validator)

    def _fetch_resource(self, ridentifier: str):
        """Obtém o recurso ou levanta exceção ``exceptions.IdDoesNotExistError``.
        """
        try:
            return self.ds.get(ridentifier)
        except datastores.DoesNotExistError:
            raise exceptions.IdDoesNotExistError('could not fetch resource with'
                    ' ridentifier: "%s"' % ridentifier)

    def _resource_exists(self, ridentifier: str) -> bool:
        try:
            _ = self._fetch_resource(ridentifier)
        except exceptions.IdDoesNotExistError:
            return False
        return True

    @check_request_args(functools.partial(are_equal, ['verb']))
    def identify(self, oairequest: OAIRequest) -> bytes:
        return serialize_identify(self.metadata, oairequest)

    @check_request_args(functools.partial(are_equal, 
        ['verb', 'metadataPrefix', 'identifier']))
    def get_record(self, oairequest: OAIRequest) -> bytes:
        if oairequest.metadataPrefix not in self.formats:
            raise exceptions.CannotDisseminateFormatError()

        fmt = self.formats[oairequest.metadataPrefix]
        resource = fmt['augmenter'](self._fetch_resource(oairequest.identifier))
        return serialize_get_record(self.metadata, oairequest, resource,
                metadata_formatter=fmt['formatter'])

    @check_request_args(check_listrecords_args)
    def list_records(self, oairequest: OAIRequest) -> bytes:
        if not oairequest.resumptionToken:
            if oairequest.metadataPrefix not in self.formats:
                raise exceptions.CannotDisseminateFormatError()

        resultpage = self._resultpage(oairequest)
        fmt = resultpage.select_format(self.formats)
        resources = [fmt['augmenter'](r) for r in resultpage.data]

        next_token = resultpage.next_resumption_token()
        return serialize_list_records(self.metadata, oairequest, resources,
                next_token, metadata_formatter=fmt['formatter'])

    @check_request_args(check_listrecords_args)
    def list_identifiers(self, oairequest: OAIRequest) -> bytes:
        if not oairequest.resumptionToken:
            if oairequest.metadataPrefix not in self.formats:
                raise exceptions.CannotDisseminateFormatError()

        resultpage = self._resultpage(oairequest)
        resources = resultpage.data

        next_token = resultpage.next_resumption_token()
        return serialize_list_identifiers(self.metadata, oairequest, resources,
                next_token)

    @check_request_args(check_listmetadataformats_args)
    def list_metadata_formats(self, oairequest: OAIRequest) -> bytes:
        if oairequest.identifier and not self._resource_exists(oairequest.identifier):
            raise exceptions.IdDoesNotExistError()

        fmts = [fmt['metadata'] for fmt in self.formats.values()]
        return serialize_list_metadata_formats(self.metadata, oairequest, fmts)

    @check_request_args(check_listsets_args)
    def list_sets(self, oairequest: OAIRequest) -> bytes:
        resultpage = self._resultpage(oairequest)
        next_token = resultpage.next_resumption_token()
        return serialize_list_sets(self.metadata, oairequest, resultpage.data,
                next_token)


def clean_oairequest_verb(oairequest: OAIRequest):
    new_values = {}
    if oairequest.verb not in ['Identify', 'ListSets', 'ListRecords',
            'ListMetadataFormats', 'ListIdentifiers', 'GetRecord']:
        new_values['verb'] = None
    return oairequest._replace(**new_values)


def clean_oairequest_dates(oairequest: OAIRequest, validator):
    new_values = {}
    if oairequest.from_ and not validator(oairequest.from_):
        new_values['from_'] = None
    if oairequest.until and not validator(oairequest.until):
        new_values['until'] = None
    return oairequest._replace(**new_values)


def now_datestamp():
    return datetime.today().isoformat()[:10]


class ResultPageFactory:
    def __init__(self, ds, setsreg, listslen, granularity_validator,
            earliest_datestamp):
        self.ds = ds
        self.setsreg = setsreg
        self.listslen = listslen
        self.granularity_validator = granularity_validator
        self.earliest_datestamp = earliest_datestamp

    def __call__(self, oairequest: OAIRequest):
        if oairequest.verb in ['ListRecords', 'ListIdentifiers']:
            return RecordsResultPage(oairequest=oairequest, ds=self.ds,
                    setsreg=self.setsreg, listslen=self.listslen,
                    granularity_validator=self.granularity_validator,
                    earliest_datestamp=self.earliest_datestamp)
        elif oairequest.verb == 'ListSets':
            return SetsResultPage(oairequest=oairequest,
                    setsreg=self.setsreg, listslen=self.listslen)
        else:
            raise ValueError('cannot handle verb "%s"' % oairequest.verb)


class SetsResultPage:
    """Representa uma página de resultados de nomes de conjuntos.
    """
    def __init__(self, oairequest: OAIRequest,
            setsreg: sets.SetsRegistry, listslen: int,
            resumption_token_factory=PlainResumptionToken):
        self.oairequest = oairequest
        self.setsreg = setsreg
        self.listslen = listslen
        self.resumption_token_factory = resumption_token_factory

    @utils.lazyproperty
    def _current_resumption_token(self):
        """Resumption token para obter o conjunto de dados atual.
        """
        return self.resumption_token_factory.new_from_request(self.oairequest,
                self.listslen)

    def next_resumption_token(self):
        """Resumption token para obter o conjunto de dados subsequente.
        """
        return self._current_resumption_token.next(self.data)

    @utils.lazyproperty
    def data(self):
        token = self._current_resumption_token
        return list(self.setsreg.list(token.query_offset(), token.query_count()))


class RecordsResultPage:
    """Representa uma página de resultados de registros ou identificadores.
    """
    def __init__(self, oairequest: OAIRequest, ds:datastores.DataStore,
            setsreg: sets.SetsRegistry, listslen: int,
            granularity_validator: Callable,
            earliest_datestamp: str,
            resumption_token_factory=ChunkedResumptionToken,
            make_default_until=now_datestamp):
        self.oairequest = oairequest
        self.ds = ds
        self.setsreg = setsreg
        self.listslen = listslen
        self.granularity_validator = granularity_validator
        self.resumption_token_factory = resumption_token_factory
        self.earliest_datestamp = earliest_datestamp
        self.make_default_until = make_default_until

    @utils.lazyproperty
    def _current_resumption_token(self):
        """Resumption token para obter o conjunto de dados atual.
        """
        earliest_datestamp = self.earliest_datestamp
        try:
            default_from = earliest_datestamp.strftime('%Y-%m-%d')
        except AttributeError:
            default_from = earliest_datestamp

        return self.resumption_token_factory.new_from_request(self.oairequest,
                self.listslen, default_from=default_from,
                default_until=self.make_default_until())

    def next_resumption_token(self):
        """Resumption token para obter o conjunto de dados subsequente.
        """
        return self._current_resumption_token.next(self.data)

    def select_format(self, formats):
        """Seleciona, dentre a coleção ``formats``, o formato que deve ser
        aplicado ao conjunto de dados.
        """
        token = self._current_resumption_token
        return formats[token.metadataPrefix]

    def _get_query_view(self):
        """Obtém a função-view associada à requisição. Retorna ``None`` caso
        nenhuma tenha sido especificada no *resumption token*. Levanta
        ``exceptions.BadArgumentError`` no caso de um nome desconhecido.
        """
        token = self._current_resumption_token
        if token.set:
            view = self.setsreg.get_view(token.set)
            if view is None:
                raise exceptions.BadArgumentError('cannot find a view for set "%s"', token.set)
        else:
            view = None

        return view

    def _ensure_datestamps_are_valid(self):
        """Garante que a granularidade e intervalos das datas ``from_`` e
        ``until`` são válidos. Levanta ``exceptions.BadArgumentError`` caso
        algum valor não seja válido; no caso contrário retorna ``None``.
        """
        token = self._current_resumption_token
        if token.from_ and not self.granularity_validator(token.from_):
            raise exceptions.BadArgumentError('invalid granularity')

        if token.until and not self.granularity_validator(token.until):
            raise exceptions.BadArgumentError('invalid granularity')

        if (token.from_ and token.until) and (token.from_ > token.until):
            raise exceptions.BadArgumentError('invalid range for datestamps')

    def _query_resources_by_token(self):
        token = self._current_resumption_token
        view = self._get_query_view()

        return self._query_resources(offset=token.query_offset(),
                count=token.query_count(), view=view,
                _from=token.query_from(), until=token.query_until())

    def _query_resources(self, offset: int, count: int,
            view: Callable[[Callable], Callable], _from: str, until: str):
        return self.ds.list(offset, count, view=view, _from=_from,
                until=until)

    @utils.lazyproperty
    def data(self):
        self._ensure_datestamps_are_valid()
        resources = [res for res in self._query_resources_by_token()]
        if self._current_resumption_token.is_first_page() and is_empty_resultset(resources):
            raise exceptions.NoRecordsMatchError()

        return resources

