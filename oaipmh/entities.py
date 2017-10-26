import re
from collections import namedtuple
from typing import (
        Type,
        TypeVar,
        Iterable,
        )

from . import exceptions


# serve apenas para type-hinting:
TResumptionToken = TypeVar('TResumptionToken', bound='ResumptionToken')


RepositoryMeta = namedtuple('RepositoryMeta', '''repositoryName baseURL
        protocolVersion adminEmail earliestDatestamp deletedRecord
        granularity''')


OAIRequest = namedtuple('OAIRequest', '''verb identifier metadataPrefix set
        resumptionToken from_ until''')


MetadataFormat = namedtuple('MetadataFormat', '''metadataPrefix schema
        metadataNamespace''')


"""
Representa um objeto de informação.

É inspirado no modelo de dados Dublin Core conforme definido originalmente em
[RFC2413]. Com exceção de ``repoidentifier`` e ``datestamp``, todos os atributos
são multivalorados, e alguns são listas associativas.
http://dublincore.org/documents/1999/07/02/dces/

sample = {
    'ridentifier': <str>,
    'datestamp': <datetime>,
    'setspec': <List[str]>,
    'title': <List[Tuple[str, str]]>,
    'creator': <List[str]>,
    'subject': <List[Tuple[str, str]]>,
    'description': <List[Tuple[str, str]]>,
    'publisher': <List[str]>,
    'contributor': <List[str]>,
    'date': <List[datetime]>,
    'type': <List[str]>,
    'format': <List[str]>,
    'identifier': <List[str]>,
    'source': <List[str]>,
    'language': <List[str]>,
    'relation': <List[str]>,
    'rights': <List[str]>,
},
res = Resource(**sample)
"""
Resource = namedtuple('Resource', '''ridentifier datestamp setspec title
        creator subject description publisher contributor date type format
        identifier source language relation rights''')


Set = namedtuple('Set', '''setSpec setName''')


class ResumptionToken:
    attrs = ['set', 'from_', 'until', 'offset', 'count', 'metadataPrefix']
    token_patterns = {
            'ListRecords': r'^(\w+)?:((\d{4})-(\d{2})-(\d{2}))?:((\d{4})-(\d{2})-(\d{2}))?:\d+:\d+:\w+$',
            'ListIdentifiers': r'^(\w+)?:((\d{4})-(\d{2})-(\d{2}))?:((\d{4})-(\d{2})-(\d{2}))?:\d+:\d+:\w+$',
            'ListSets': r'^:((\d{4})-(\d{2})-(\d{2}))?:((\d{4})-(\d{2})-(\d{2}))?:\d+:\d+:$',
            }

    def __init__(self, **kwargs):
        for attr in self.attrs:
            setattr(self, attr, kwargs.get(attr, None))

    @classmethod
    def new_from_request(cls: Type[TResumptionToken], oairequest: OAIRequest,
            default_count: int) -> TResumptionToken:
        """Obtém um ``ResumptionToken`` à partir do ``oairequest``.

        Caso o token não seja válido sintaticamente ou o valor do atributo ``count``
        seja diferente de ``default_count``, levanta a exceção ``BadResumptionToken``;
        Retorna um novo ``ResumptionToken`` caso não haja um codificado no
        ``oairequest``.
        """
        if oairequest.resumptionToken:
            if not cls.is_valid_oairequest(oairequest):
                raise exceptions.BadResumptionTokenError()

            token = cls.decode(oairequest.resumptionToken)
            if int(token.count) != default_count:
                raise exceptions.BadResumptionTokenError('token count is different than ``oaipmh.listslen``')
        else:
            token = cls(set=oairequest.set, from_=oairequest.from_,
                    until=oairequest.until, offset='0', count=str(default_count),
                    metadataPrefix=oairequest.metadataPrefix)

        return token

    @classmethod
    def decode(cls: Type[TResumptionToken], token: str) -> TResumptionToken:
        keys = cls.attrs
        values = token.split(':')
        kwargs = dict(zip(keys, values))
        return cls(**kwargs)

    @classmethod
    def is_valid_token(cls: Type[TResumptionToken], token: str,
            pattern: str) -> bool:
        """Se o valor de ``token`` é válido sintaticamente.
        """
        return bool(re.fullmatch(pattern, token))

    @classmethod
    def get_validation_pattern(cls, verb: str) -> str:
        try:
            return cls.token_patterns[verb]
        except KeyError:
            raise ValueError() from None

    @classmethod
    def is_valid_oairequest(cls: Type[TResumptionToken],
            oairequest: OAIRequest) -> bool:
        pattern = cls.get_validation_pattern(oairequest.verb)
        return cls.is_valid_token(oairequest.resumptionToken,
                pattern)

    def encode(self) -> str:
        """Codifica o token em string delimitada por ``:``.

        Durante a codificação, todos os valores serão transformados em ``str``.
        ``None`` será transformado em string vazia. 

        É importante ter em mente que o processo de codificação faz com que os
        tipos originais dos valores sejam perdidos, i.e., não é um processo
        reversível.
        """
        def ensure_str(obj):
            if obj is None:
                return ''
            else:
                try:
                    return str(obj)
                except:
                    return ''
        token = [getattr(self, attr) for attr in self.attrs]
        parts = [ensure_str(part) for part in token]
        return ':'.join(parts)

    def _incr_offset(self) -> TResumptionToken:
        """Avança o offset do token.
        """
        token_map = self._asdict()
        new_offset = 1 + int(token_map['offset']) + int(token_map['count'])
        token_map['offset'] = str(new_offset)
        return self.__class__(**token_map)

    def next(self, resources: Iterable) -> TResumptionToken:
        """Retorna o próximo resumption token com base no atual e seq de
        ``resources`` resultado da requisição corrente.
        """
        if self._has_more_resources(resources, self.count):
            return self._incr_offset()
        else:
            return None

    def _has_more_resources(self, resources: Iterable, batch_size: int) -> bool:
        """Verifica se ``resources`` completa a lista de recursos.

        Se a quantidade de itens em ``resources`` for menor do que ``batch_size``, 
        consideramos se tratar do último conjunto de resultados. Caso a 
        quantidade seja igual, consideramos que existirá o próximo conjunto.
        """
        return len(resources) == int(batch_size)

    def _asdict(self) -> dict:
        """Atua como uma ``namedtuple``, na produção de um dicionário à partir
        de si mesmo.
        """
        return {attr: getattr(self, attr) for attr in self.attrs}

    def __hash__(self):
        return hash((self.__class__, self.encode()))

    def __eq__(self, obj):
        return hash(self) == hash(obj)

    def __repr__(self):
        return '<%s with values %s>' % (self.__class__.__name__, self._asdict())


