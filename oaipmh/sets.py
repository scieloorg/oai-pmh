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
from collections import namedtuple, OrderedDict
import itertools

from .datastores import ArticleMetaFilteredView


Set = namedtuple('Set', '''setSpec setName''')


class SetsRegistry:
    """O registro de ``Set``s da aplicação.

    :param ds: instância de ``oaipmh.datastores.DataStore``.
    :param static_defs: lista associativa de objetos ``Set`` e funções ``view``.
    """
    def __init__(self, ds, static_defs):
        self.ds = ds
        self.static_sets = [s for s, _ in static_defs]
        self.static_views = {s.setSpec: v for s, v in static_defs}

    def list(self, offset, count):
        """Retorna sequência com ``count`` instâncias de ``Set`` à partir de
        ``offset``.
        """
        static_part = self.static_sets[offset:offset+count]
        if len(static_part) < count:
            dynamic_part = get_sets_from_journals(self.ds,
                    translate_virtual_offset(len(self.static_sets), offset),
                    count - len(static_part))
        else:
            dynamic_part = []

        return itertools.chain(static_part, dynamic_part)

    def get_view(self, setspec):
        """Retorna a ``view`` associada ao ``setspec``.
        """
        try:
            return self.static_views[setspec]
        except KeyError:
            return get_view_for_journal_set(get_set_from_journal(self.ds, setspec))


def translate_virtual_offset(size, offset):
    """Despreza o intervalo ``size`` em ``offset`` correspondente aos sets
    estáticos, retornando um novo ``offset`` que pode ser utilizado na consulta
    aos sets dinâmicos.
    """
    real_offset = offset - size 
    if real_offset <= 0:
        return 0
    else:
        return real_offset


def get_sets_from_journals(ds, offset, count):
    """Sequência de ``Set`` à partir de periódicos da fonte de dados ``ds``.
    """
    journals = ds.list_journals(offset, count)
    return (map_journal_to_set(j) for j in journals)


def get_set_from_journal(ds, issn):
    """``Set`` à partir de periódico da fonte de dados ``ds``.
    """
    journal = ds.get_journal(issn)
    return map_journal_to_set(journal)


def map_journal_to_set(journal):
    """``Set`` à partir de ``oaipmh.datastores.Journal``.
    """
    return Set(setSpec=journal.lead_issn, setName=journal.title)


def get_view_for_journal_set(set_):
    """Obtém uma função ``view`` que aplica filtro por registros do periódico
    representado por ``set_``.
    """
    view = ArticleMetaFilteredView({'code_title': set_.setSpec})
    return view

