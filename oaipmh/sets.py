"""
Deve ser possível:
  * Estruturar os conjuntos de forma hierárquica;
  * Acrescentar novos conjuntos sem que haja refatoração; Design para extensão;
  * Representar conjuntos dinâmicos (aqueles que podem ser acrescentados
    durante a execução do programa como resultado da inclusão de novos registros.
    São conjuntos que agrupam registros pelo valor de determinado atributo.
    e.g.: ISSN, tipo de documento, ano de publicação etc);
  * Representar conjuntos estáticos (definidos no momento da compilação pelo
    programador);
  * Listar os diversos conjuntos disponibilizados pelo repositório;
  * Sinalizar nos registros os conjuntos os quais estão contidos;
  * Consultar os registros contidos em um conjunto;
  
"""
import abc
import itertools
from typing import (
        Callable,
        Iterable,
        Tuple,
        )
from collections import OrderedDict

from .entities import Set
from .datastores import DoesNotExistError  


class SetsRegistry(metaclass=abc.ABCMeta):
    """O registro de ``Set``s da aplicação.
    """
    @abc.abstractmethod
    def add(self, metadata: Set, view: Callable[[Callable], Callable]) -> None:
        """Registra os conjuntos suportados pelo repositório.

        :param metadata: descreve o conjunto.
        :param view: função de ordem superior passada como argumento para o método
        ``DataStore.list``, responsável por receber e produzir a função de
        consulta aos dados dos recursos.
        """
        return NotImplemented

    @abc.abstractmethod
    def list(self, offset: int, count: int) -> Iterable[Set]:
        """Retorna sequência com ``count`` instâncias de ``Set`` à partir de
        ``offset``.
        """
        return NotImplemented

    @abc.abstractmethod
    def get_view(self, setspec: str) -> Tuple[Callable, Callable]:
        """Retorna a função ``view`` associada ao ``setspec``.
        """
        return NotImplemented


class InMemory(SetsRegistry):
    def __init__(self):
        self.sets = OrderedDict()

    def add(self, metadata, view):
        self.sets[metadata.setSpec] = (metadata, view)

    def list(self, offset, count):
        return list(self.sets.values())[offset:offset+count]

    def get_view(self, setspec):
        try:
            return self.sets[setspec][1]
        except KeyError:
            return None

