from collections import namedtuple


RepositoryMeta = namedtuple('RepositoryMeta', '''repositoryName baseURL
        protocolVersion adminEmail earliestDatestamp deletedRecord
        granularity''')


OAIRequest = namedtuple('OAIRequest', '''verb identifier metadataPrefix set
        resumptionToken from_ until''')


MetadataFormat = namedtuple('MetadataFormat', '''metadataPrefix schema
        metadataNamespace''')


ResumptionToken = namedtuple('ResumptionToken', '''set from_ until offset count
        metadataPrefix''')


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

