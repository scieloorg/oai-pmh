
class BadArgumentError(Exception):
    """A requisição contém argumentos ilegais, argumentos faltantes,
    argumentos repetidos ou valores sintaticamente inválidos.
    """


class BadResumptionTokenError(Exception):
    """Lançada quando o valor do argumento ``resumptionToken`` é inválido ou 
    expirou.
    """


class CannotDisseminateFormatError(Exception):
    """O formato identificado pelo valor do argumento ``metadataPrefix`` não é
    suportado pelo item ou pelo repositório.
    """


class IdDoesNotExistError(Exception):
    """O valor do argumento ``identifier`` é desconhecido ou ilegal no contexto
    do repositório.
    """


class NoRecordsMatchError(Exception):
    """A combinação dos valores dos argumentos ``from``, ``until``, ``set`` e
    ``metadataPrefix`` resulta em uma lista vazia.
    """
