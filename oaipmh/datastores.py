import abc
from typing import List, Iterable
from collections import namedtuple
import itertools
import datetime


from articlemeta import client as articlemeta_client


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


class DoesNotExistError(Exception):
    """Quando nenhum recurso corresponde ao ``ridentifier`` informado.
    """


class DataStore(metaclass=abc.ABCMeta):
    """Encapsula o acesso a um sistema ou recurso externo.

    Saiba mais em https://martinfowler.com/eaaCatalog/gateway.html
    """
    @abc.abstractmethod
    def add(self, resource: Resource) -> None:
        """Adiciona o recurso ``resource``.
        """ 
        return NotImplemented

    @abc.abstractmethod
    def get(self, ridentifier: str) -> Resource:
        """Recupera o recurso associado a ``ridentifier``.
        """
        return NotImplemented

    @abc.abstractmethod
    def list(self, sets: List[str] = None, offset: int = 0,
            count: int = 1000, _from: str = None, 
            until: str = None) -> Iterable[Resource]:
        """Produz uma coleção dos recursos contidos em todos os ``sets``.

        Os argumentos ``offset`` e ``count`` permitem que o a coleção seja 
        produzida por partes.
        """
        return NotImplemented


def datestamp_to_tuple(datestamp):
    return tuple(map(int, datestamp.split('-')))


class InMemory(DataStore):
    def __init__(self):
        self.data = {}

    def add(self, resource):
        self.data[resource.ridentifier] = resource

    def get(self, ridentifier):
        try:
            return self.data[ridentifier]
        except KeyError:
            raise DoesNotExistError() from None

    def list(self, sets=None, offset=0, count=1000, _from=None, until=None):
        ds2tup = datestamp_to_tuple
        sets = set(sets) if sets else set()

        ds = self.data.values()
        if sets:
            ds = (res for res in ds if sets.intersection(set(res.setspec)))
        if _from:
            ds = (res for res in ds if ds2tup(res.datestamp) >= ds2tup(_from))
        if until:
            ds = (res for res in ds if ds2tup(res.datestamp) < ds2tup(until))

        ds = (res for i, res in enumerate(ds) if i >= offset)
        ds = (res for i, res in enumerate(ds) if i < count)
        yield from ds
        

class SliceableResultSetThriftClient(articlemeta_client.ThriftClient):
    """Altera o comportamento do método ``documents`` para que seja possível
    controlar os argumentos ``limit`` e ``offset`` na consulta ao backend.
    """
    def __documents_ids(self, collection=None, issn=None, from_date=None,
            until_date=None, extra_filter=None, limit=None, offset=None):
        limit = limit or articlemeta_client.LIMIT
        offset = offset or 0

        try:
            with self.client_context() as client:
                identifiers = client.get_article_identifiers(
                    collection=collection, issn=issn,
                    from_date=from_date, until_date=until_date,
                    limit=limit, offset=offset,
                    extra_filter=extra_filter)
        except self.ARTICLEMETA_THRIFT.ServerError:
            msg = 'Error retrieving list of article identifiers: %s_%s' % (collection, issn)
            raise articlemeta_client.ServerError(msg)

        if len(identifiers) == 0:
            return

        for identifier in identifiers:
            yield identifier


    def documents(self, collection=None, issn=None, from_date=None,
                  until_date=None, fmt='xylose', body=False, extra_filter=None,
                  only_identifiers=False, limit=None, offset=None):
        identifiers = self.__documents_ids(collection=collection, issn=issn,
                from_date=from_date, until_date=until_date,
                extra_filter=extra_filter, limit=limit, offset=offset)
        for identifier in identifiers:
            if only_identifiers:
                yield identifier
            else:
                document = self.document(
                    identifier.code,
                    identifier.collection,
                    replace_journal_metadata=False,
                    fmt=fmt,
                    body=body
                )
                yield document


class BoundArticleMetaClient:
    """Cliente da API ArticleMeta cujas consultas são vinculadas ao conteúdo
    de determinada coleção.
    """
    def __init__(self, client, collection):
        self.client = client
        self.collection = collection

    def document(self, code):
        return self.client.document(code, self.collection)

    def documents(self, issn=None, from_date=None, until_date=None,
            offset=0, limit=1000):
        return self.client.documents(collection=self.collection, issn=issn,
                from_date=from_date, until_date=until_date, offset=offset,
                limit=limit)


def get_articlemeta_client(collection, **kwargs):
    """Retorna um cliente do serviço ArticleMeta otimizado e adaptado para
    uso como DataStore.
    """
    thriftclient = SliceableResultSetThriftClient(**kwargs)
    adaptedclient = BoundArticleMetaClient(thriftclient, collection)
    return adaptedclient


def parse_date(datestamp):
    fmts = ['%Y-%m-%d', '%Y-%m', '%Y']
    for fmt in fmts:
        try:
            return datetime.datetime.strptime(datestamp, fmt)
        except ValueError:
            continue
    else:
        raise ValueError("time data '%s' does not match formats '%s'" % (
            datestamp, fmts))


class ArticleResourceFacade:
    def __init__(self, article):
        self.article = article

    def ridentifier(self):
        return self.article.publisher_id

    def datestamp(self):
        return parse_date(self.article.processing_date)

    def setspec(self):
        return [issn for issn in [getattr(self.article, attr)
                  for attr in ['electronic_issn', 'print_issn']]
                if issn]

    def title(self):
        art = self.article
        titles = [(art.original_language(), art.original_title())]

        translated_titles = art.translated_titles()
        if translated_titles:
            titles += translated_titles.items()
        return titles

    def creator(self):
        authors = self.article.authors
        if authors:
            return [', '.join([author.get('surname', ''), author.get('given_names', '')])
                    for author in authors]
        else:
            return []

    def subject(self):
        subjects = []

        keywords = self.article.keywords()
        if keywords:
            for lang, kwds in keywords.items():
                for kwd in kwds:
                    subjects.append((lang, kwd))

        return subjects

    def description(self):
        art = self.article
        abstracts = [(art.original_language(), art.original_abstract())]

        translated_abstracts = art.translated_abstracts()
        if translated_abstracts:
            abstracts += translated_abstracts.items()

        return abstracts

    def publisher(self):
        return self.article.journal.publisher_name

    def contributor(self):
        return []

    def date(self):
        pubdate = parse_date(self.article.publication_date)
        return [pubdate]

    def type(self):
        typ = self.article.document_type
        return [typ]

    def format(self):
        return ['text/html']

    def identifier(self):
        html_url = self.article.html_url()
        return [html_url]

    def source(self):
        """Algo tipo: ['Revista de Microbiologia v.29 n.3 1998']
        """
        return []

    def language(self):
        lang = self.article.original_language()
        return [lang]

    def relation(self):
        return []

    def rights(self):
        license_url = self.article.permissions.get('url', '')
        return [license_url]

    def to_resource(self):
        return Resource(ridentifier=self.ridentifier(),
                        datestamp=self.datestamp(),
                        setspec=self.setspec(),
                        title=self.title(),
                        creator=self.creator(),
                        subject=self.subject(),
                        description=self.description(),
                        publisher=self.publisher(),
                        contributor=self.contributor(),
                        date=self.date(),
                        type=self.type(),
                        format=self.format(),
                        identifier=self.identifier(),
                        source=self.source(),
                        language=self.language(),
                        relation=self.relation(),
                        rights=self.rights())


def is_spurious_doc(doc):
    """Instâncias de ``xylose.scielodocument.Article`` são produzidas pelo
    articlemetaapi mesmo para consultas a documentos que não existem.
    """
    try:
        doc.original_language()
    except TypeError:
        return True
    else:
        return False


class ArticleMeta(DataStore):
    def __init__(self, client: BoundArticleMetaClient):
        self.client = client

    def add(self, resource):
        return NotImplemented

    def get(self, ridentifier):
        doc = self.client.document(ridentifier)
        if is_spurious_doc(doc):
            raise DoesNotExistError()
        return ArticleResourceFacade(doc).to_resource()

    def list(self, sets=None, offset=0, count=1000, _from=None, until=None):
        docs = self.client.documents(offset=offset, limit=count,
                from_date=_from, until_date=until)
        return (ArticleResourceFacade(doc).to_resource()
                for doc in docs)

