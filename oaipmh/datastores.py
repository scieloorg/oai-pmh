import abc
from typing import (
        Iterable,
        Callable,
        Dict,
        )

from .entities import Resource


class DoesNotExistError(Exception):
    """Quando nenhum recurso corresponde ao ``ridentifier`` informado.
    """


class ViewDoesNotExistError(Exception):
    """Quando se tenta recuperar uma view que não existe em um repositório.
    """


def identityview(f):
    """Retorna a função que recebeu como argumento, inalterada.
    """
    return f


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
    def list(self, offset: int, count: int, view: Callable=None, 
            _from: str=None, until: str=None) -> Iterable[Resource]:
        """Produz uma coleção de objetos ``Resource``.

        Os argumentos ``offset`` e ``count`` permitem o retorno de partes
        do resultado da consulta.
        :param view: (opcional) função de ordem superior para a filtragem de 
        registros. caso não informada, a consulta se dará sob todos os registros.
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

    def list(self, offset, count, view=None, _from=None, until=None):
        ds2tup = datestamp_to_tuple
        view_fn = view or identityview
        query_fn = view_fn(self.data.values)

        ds = query_fn()
        if _from:
            ds = (res for res in ds if ds2tup(res.datestamp) >= ds2tup(_from))
        if until:
            ds = (res for res in ds if ds2tup(res.datestamp) < ds2tup(until))

        ds = (res for i, res in enumerate(ds) if i >= offset)
        ds = (res for i, res in enumerate(ds) if i < count)
        yield from ds

