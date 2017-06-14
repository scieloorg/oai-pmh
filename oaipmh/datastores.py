import abc
from typing import List, Iterable
from collections import namedtuple
import itertools


"""
Representa um objeto de informação.

É inspirado no modelo de dados Dublin Core conforme definido originalmente em
[RFC2413]. Com exceção de ``repoidentifier`` e ``datestamp``, todos os atributos
são multivalorados, e alguns são listas associativas.
http://dublincore.org/documents/1999/07/02/dces/

sample = {
    'ridentifier': 'oai:arXiv:cs/0112017',
    'datestamp': '2017-06-14',
    'setspec': ['set1', 'set2'],
    'title': [('en', 'MICROBIAL COUNTS OF DARK RED...')],
    'creator': ['Vieira, Francisco Cleber Sousa'],
    'subject': [('en', 'bacteria'), ('pt', 'bactéria')],
    'description': [('en', 'The number of colony forming units (CFU)...')],
    'publisher': ['Sociedade Brasileira de Microbiologia'],
    'contributor': ['Evans, R. J.'],
    'date': ['1998-09-01'],
    # does not comply with DCMI vocabulary
    'type': ['research-article'],
    'format': ['text/html'],
    'identifier': ['https://ref.scielo.org/7vy47j'],
    'source': ['Revista de Microbiologia v.29 n.3 1998'],
    'language': ['en'],
    # the identifier of another record or resource
    'relation': [],
    'rights': ['http://creativecommons.org/licenses/by-nc/4.0/'],
    }
res = Resource(**sample)
"""
Resource = namedtuple('Resource', '''ridentifier datestamp setspec title
        creator subject description publisher contributor date type format
        identifier source language relation rights ''')


class DoesNotExistError(Exception):
    """Quando nenhum recurso corresponde ao ``ridentifier`` informado.
    """


class DataStore(metaclass=abc.ABCMeta):
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
            count: int = 1000) -> Iterable[Resource]:
        """Produz uma coleção dos recursos contidos em todos os ``sets``.

        Os argumentos ``offset`` e ``count`` permitem que o a coleção seja 
        produzida por partes.
        """
        return NotImplemented


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

    def list(self, sets=None, offset=0, count=1000):
        sets = set(sets) if sets else set()
        c = 0  # total de resources produzidos
        for i, resource in enumerate(self.data.values()):
            if i < offset or (sets and not sets.intersection(
                set(resource.setspec))):
                continue
            elif c >= count:
                return
            else:
                c += 1
                yield resource

